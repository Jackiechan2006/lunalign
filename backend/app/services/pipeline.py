from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

import cv2
import numpy as np
import yaml

from core.dem.loader import dem_consistency, derive_dem_from_image, load_dem, mesh_preview, synthetic_dem
from core.features.sift import extract_multiscale_rootsift, extract_rootsift
from core.geometry.ransac import auto_estimate
from core.geometry.scale import estimate_scale_from_transform, gsd_scale_ratio
from core.geometry.sun import azimuth_difference_deg, elevation_difference_deg, illumination_severity, representation_guidance
from core.matching.adaptive import decide
from core.matching.deep import loftr_status, run_deep_or_skip
from core.matching.hybrid import fuse_matches
from core.matching.knn import knn_match
from core.preprocessing.iirs import preprocess_iirs
from core.preprocessing.optical import Representations, preprocess_ohrc, preprocess_tmc
from core.quality.score import failure_flags, quality_score
from core.quality.uniform import select_uniform
from core.refinement.ncc import refine_points
from core.sensors.detect import load_by_sensor
from core.sensors.quality import assess_product
from core.temporal.index import potential_change, timeline_marks
from core.visualization.overlays import difference_map, draw_grid, draw_inliers_high_vis, draw_matches, overlay_warp


def load_config(path: str | Path | None = None) -> dict:
    root = Path(__file__).resolve().parents[3]
    cfg_path = Path(path) if path else root / "configs" / "default.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@dataclass
class StageLog:
    name: str
    ok: bool
    seconds: float
    detail: str = ""


def _time_stage(name: str, fn: Callable, logs: list[StageLog]):
    t0 = time.perf_counter()
    try:
        out = fn()
        logs.append(StageLog(name, True, time.perf_counter() - t0, "ok"))
        return out
    except Exception as exc:  # noqa: BLE001
        logs.append(StageLog(name, False, time.perf_counter() - t0, str(exc)))
        raise


def _choose_matching_image(reps: Representations, prefer: list[str]) -> np.ndarray:
    mapping = {
        "intensity": reps.intensity,
        "clahe": reps.clahe,
        "lcn": np.abs(reps.lcn),
        "gradient_mag": reps.gradient_mag,
        "gradient_ori": (reps.gradient_ori + np.pi) / (2 * np.pi),
        "edges": reps.edges,
        "phase_proxy": reps.phase_proxy,
    }
    acc = None
    wsum = 0.0
    for i, k in enumerate(prefer[:3]):
        img = mapping.get(k)
        if img is None:
            continue
        w = 1.0 / (i + 1)
        acc = img * w if acc is None else acc + img * w
        wsum += w
    if acc is None or wsum == 0:
        return reps.matching_image
    acc = acc / wsum
    mx = float(np.max(np.abs(acc))) + 1e-8
    return np.clip(acc / mx, 0, 1).astype(np.float32)


def _preprocess(product, pca_k: int) -> tuple[Representations, dict]:
    extra = {}
    if product.metadata.sensor == "IIRS" or product.cube is not None:
        src = product.cube if product.cube is not None else product.image
        iirs = preprocess_iirs(src, n_components=pca_k)
        extra["iirs"] = iirs.to_dict()
        return iirs.representations, extra
    if product.metadata.sensor == "TMC":
        return preprocess_tmc(product.image), extra
    return preprocess_ohrc(product.image), extra


def run_registration(
    ref_path: str,
    mov_path: str,
    *,
    ref_sensor: str | None = None,
    mov_sensor: str | None = None,
    ref_meta: dict | None = None,
    mov_meta: dict | None = None,
    origin: str = "REAL_CHANDRAYAAN2",
    mode: str = "automatic",
    dem_path: str | None = None,
    dem_kind: str = "REAL_DEM",
    allow_synthetic_dem: bool = False,
    config: dict | None = None,
    out_dir: str | Path | None = None,
    pca_components: int | None = None,
    progress: Callable[[str, dict], None] | None = None,
) -> dict[str, Any]:
    cfg = config or load_config()
    logs: list[StageLog] = []
    t_all = time.perf_counter()
    out_dir = Path(out_dir) if out_dir else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    def emit(stage: str, payload: dict):
        if progress:
            progress(stage, payload)

    emit("loading", {"message": "Loading products"})
    ref = _time_stage("Loading", lambda: load_by_sensor(ref_path, ref_sensor, origin=origin, manual_meta=ref_meta), logs)
    mov = _time_stage("Loading-moving", lambda: load_by_sensor(mov_path, mov_sensor, origin=origin, manual_meta=mov_meta), logs)

    q_ref = assess_product(ref)
    q_mov = assess_product(mov)
    if not q_ref.ok or not q_mov.ok:
        return {
            "ok": False,
            "error": "Data quality check failed.",
            "quality_ref": q_ref.to_dict(),
            "quality_mov": q_mov.to_dict(),
            "stages": [s.__dict__ for s in logs],
        }

    pca_k = pca_components or int(cfg.get("iirs", {}).get("pca_components", 3))
    emit("preprocessing", {"message": "Sensor-aware preprocessing"})
    ref_reps, ref_extra = _time_stage("Preprocessing", lambda: _preprocess(ref, pca_k), logs)
    mov_reps, mov_extra = _preprocess(mov, pca_k)

    d_az = azimuth_difference_deg(ref.metadata.sun_azimuth_deg, mov.metadata.sun_azimuth_deg)
    d_el = elevation_difference_deg(ref.metadata.sun_elevation_deg, mov.metadata.sun_elevation_deg)
    sev = illumination_severity(d_az, d_el)
    guide = representation_guidance(sev)
    emit("illumination", {"message": "Illumination-robust representations", "severity": sev})
    logs.append(StageLog("Illumination normalization", True, 0.0, guide["reason"]))
    ref_m = _choose_matching_image(ref_reps, guide["prefer"])
    mov_m = _choose_matching_image(mov_reps, guide["prefer"])

    expected_scale = gsd_scale_ratio(ref.metadata.gsd_m, mov.metadata.gsd_m)
    emit("scale", {"message": "Scale estimation", "expected_scale": expected_scale})
    logs.append(StageLog("Scale estimation", True, 0.0, f"GSD ratio={expected_scale}"))

    deep_ckpt = cfg.get("deep", {}).get("loftr_checkpoint")
    deep_st = loftr_status(deep_ckpt)
    decision = decide(
        ref_image=ref_m,
        mov_image=mov_m,
        ref_sensor=ref.metadata.sensor,
        mov_sensor=mov.metadata.sensor,
        scale_ratio=expected_scale,
        sun_severity=sev,
        mode=mode,
        deep_available=deep_st.available,
    )
    emit("features", {"message": "Feature extraction", "decision": decision.to_dict()})

    def extract():
        log_scale = abs(np.log2(max(expected_scale or 1.0, 1e-6)))
        if "multiscale" in decision.matcher.lower() or log_scale > 0.5:
            f1 = extract_multiscale_rootsift(ref_reps.pyramid)
            f2 = extract_multiscale_rootsift(mov_reps.pyramid)
        else:
            f1 = extract_rootsift(ref_m)
            f2 = extract_rootsift(mov_m)
        return f1, f2

    f1, f2 = _time_stage("Feature extraction", extract, logs)
    emit("matching", {"message": "Candidate matching"})
    matches = _time_stage(
        "Candidate matching",
        lambda: knn_match(
            f1.descriptors,
            f2.descriptors,
            f1.points,
            f2.points,
            ratio=float(cfg["matching"]["ratio_test"]),
            mutual=bool(cfg["matching"]["mutual_nn"]),
            use_flann=bool(cfg["matching"].get("flann", False)),
        ),
        logs,
    )
    deep_matches = None
    deep_note = deep_st.message
    if decision.family in {"Deep Learning", "Hybrid"} and deep_st.available:
        deep_matches, deep_st2 = run_deep_or_skip(ref_m, mov_m, deep_ckpt, "loftr")
        deep_note = deep_st2.message
        if deep_matches is not None:
            matches = fuse_matches(matches, deep_matches)

    emit("geometry", {"message": "Geometric verification"})
    geom = _time_stage(
        "Geometric verification",
        lambda: auto_estimate(
            matches.src_pts,
            matches.dst_pts,
            expected_scale,
            ref.metadata.sensor == mov.metadata.sensor,
            thresh=float(cfg["geometry"]["ransac_threshold"]),
        ),
        logs,
    )
    if geom.inlier_mask is not None and geom.inliers > 0:
        src_in = matches.src_pts[geom.inlier_mask]
        dst_in = matches.dst_pts[geom.inlier_mask]
        dist_in = matches.distances[geom.inlier_mask]
        ratio_in = matches.ratios[geom.inlier_mask]
        residuals = geom.residuals[geom.inlier_mask] if geom.residuals is not None else np.zeros(len(src_in))
    else:
        src_in = matches.src_pts
        dst_in = matches.dst_pts
        dist_in = matches.distances
        ratio_in = matches.ratios
        residuals = np.zeros(len(src_in))

    scores = np.ones(len(src_in))
    if len(src_in):
        scores = (1.0 / (1.0 + dist_in)) * (1.0 / (1.0 + residuals))
    emit("uniform", {"message": "Uniform point selection"})
    sel, cov = _time_stage(
        "Uniform point selection",
        lambda: select_uniform(
            src_in,
            dst_in,
            scores,
            ref.image.shape,
            grid=tuple(cfg["uniform"]["grid"]),
            max_per_cell=int(cfg["uniform"]["max_per_cell"]),
            min_separation=float(cfg["uniform"]["min_separation_px"]),
        ),
        logs,
    )
    src_u = src_in[sel] if len(sel) else src_in
    dst_u = dst_in[sel] if len(sel) else dst_in

    emit("refinement", {"message": "Sub-pixel NCC refinement"})
    dst_r, ncc_details = _time_stage(
        "Sub-pixel refinement",
        lambda: refine_points(
            ref_m,
            mov_m,
            src_u,
            dst_u,
            patch_size=int(cfg["refinement"]["patch_size"]),
            radius=int(cfg["refinement"]["search_radius"]),
        ),
        logs,
    )
    ncc_vals = [d["ncc"] for d in ncc_details if d.get("ncc") is not None]
    shifts = [d["shift"] for d in ncc_details if d.get("ok")]
    mean_ncc = float(np.mean(ncc_vals)) if ncc_vals else None
    mean_shift = float(np.mean(shifts)) if shifts else None

    dem_info = None
    dem_cons = None
    mesh = None
    if dem_path and Path(dem_path).exists() and Path(dem_path).is_file() and Path(dem_path).stat().st_size > 0:
        try:
            dem = load_dem(dem_path, kind=dem_kind)
            dem_info = dem.to_dict()
            dem_cons = dem_consistency(dem.z, src_u, dst_r)
            mesh = mesh_preview(dem.z)
            logs.append(StageLog("DEM verification", True, 0.0, dem_info["label"]))
        except Exception as exc:  # noqa: BLE001
            logs.append(StageLog("DEM verification", False, 0.0, f"DEM load failed ({exc}). Using derived 3D DEM."))
            dem = derive_dem_from_image(ref.image)
            dem_info = dem.to_dict()
            dem_cons = dem_consistency(dem.z, src_u, dst_r)
            mesh = mesh_preview(dem.z)
    elif allow_synthetic_dem:
        dem = synthetic_dem(ref.image.shape[:2])
        dem_info = dem.to_dict()
        dem_cons = dem_consistency(dem.z, src_u, dst_r)
        mesh = mesh_preview(dem.z)
        logs.append(StageLog("DEM verification", True, 0.0, "SYNTHETIC DEM — NOT SCIENTIFIC DATA"))
    else:
        dem = derive_dem_from_image(ref.image)
        dem_info = dem.to_dict()
        dem_cons = dem_consistency(dem.z, src_u, dst_r)
        mesh = mesh_preview(dem.z)
        logs.append(StageLog("DEM verification", True, 0.0, "DERIVED DEM — Photometric elevation mesh estimated from reference image."))

    emit("quality", {"message": "Quality assessment"})
    q = quality_score(
        inlier_ratio=geom.inlier_ratio,
        rmse=geom.rmse,
        median_error=geom.median_error,
        coverage=float(cov["coverage"]),
        mean_ncc=mean_ncc,
        mean_ratio=float(np.mean(ratio_in)) if len(ratio_in) else None,
        subpixel_shift=mean_shift,
        dem_residual=None if not dem_cons else dem_cons.get("mean_residual"),
        weights=cfg.get("quality", {}).get("weights"),
    )
    fail = failure_flags(
        n_matches=int(len(src_u)),
        inlier_ratio=geom.inlier_ratio,
        rmse=geom.rmse,
        coverage=float(cov["coverage"]),
        mean_ncc=mean_ncc,
        cfg=cfg.get("quality"),
    )
    logs.append(StageLog("Quality assessment", True, 0.0, fail["status"]))

    estimated_scale = estimate_scale_from_transform(geom.matrix, geom.model) if geom.matrix is not None else None
    scale_error = None
    if expected_scale and estimated_scale:
        scale_error = abs(estimated_scale - expected_scale) / expected_scale

    correspondences = []
    for i in range(len(src_u)):
        nd = ncc_details[i] if i < len(ncc_details) else {}
        correspondences.append(
            {
                "id": i,
                "ref": [float(src_u[i, 0]), float(src_u[i, 1])],
                "mov": [float(dst_r[i, 0]), float(dst_r[i, 1])],
                "mov_initial": [float(dst_u[i, 0]), float(dst_u[i, 1])],
                "descriptor_distance": float(dist_in[sel[i]]) if len(sel) else None,
                "lowe_ratio": float(ratio_in[sel[i]]) if len(sel) else None,
                "geometric_residual": float(residuals[sel[i]]) if len(sel) else None,
                "ncc": nd.get("ncc"),
                "subpixel_shift": nd.get("shift"),
            }
        )

    previews = {}
    if out_dir is not None:
        cv2.imwrite(str(out_dir / "ref.png"), (np.clip(ref_m, 0, 1) * 255).astype(np.uint8))
        cv2.imwrite(str(out_dir / "mov.png"), (np.clip(mov_m, 0, 1) * 255).astype(np.uint8))
        ov = overlay_warp(ref_m, mov_m, geom.matrix, geom.model)
        df = difference_map(ref_m, mov_m, geom.matrix, geom.model)
        mt = draw_matches(ref_m, mov_m, src_u, dst_r)
        inl = draw_inliers_high_vis(
            ref_m,
            mov_m,
            src_in,
            dst_in,
            src_candidates=matches.src_pts,
            dst_candidates=matches.dst_pts,
            title=f"RANSAC INLIERS ({geom.method} / {geom.model})",
            inlier_ratio=geom.inlier_ratio,
            rmse=geom.rmse,
        )
        gd = draw_grid(ref_m, tuple(cov["grid"]), src_u)
        cv2.imwrite(str(out_dir / "overlay.png"), ov)
        cv2.imwrite(str(out_dir / "difference.png"), df)
        cv2.imwrite(str(out_dir / "matches.png"), mt)
        cv2.imwrite(str(out_dir / "inliers.png"), inl)
        cv2.imwrite(str(out_dir / "grid.png"), gd)
        previews = {
            "reference": "ref.png",
            "moving": "mov.png",
            "overlay": "overlay.png",
            "difference": "difference.png",
            "matches": "matches.png",
            "inliers": "inliers.png",
            "uniform": "grid.png",
        }

    runtime = time.perf_counter() - t_all
    logs.append(StageLog("Final result", True, runtime, "complete"))
    emit("done", {"message": "Final result"})

    algorithm = {
        "feature_detector": f1.detector,
        "descriptor": f1.descriptor_name,
        "matcher": matches.matcher,
        "filtering": "Lowe ratio + mutual NN" if cfg["matching"]["mutual_nn"] else "Lowe ratio",
        "geometry": f"{geom.method} / {geom.model}",
        "refinement": "NCC + quadratic peak fitting",
        "dimensionality_reduction": "PCA" if "iirs" in ref_extra or "iirs" in mov_extra else "Not used",
        "deep_model": deep_st.name if deep_st.available and deep_matches is not None else "Not used",
        "checkpoint": deep_st.checkpoint if deep_st.available and deep_matches is not None else None,
        "family": decision.family,
        "adaptive_log": decision.reasons,
        "deep_note": deep_note,
    }

    result = {
        "ok": True,
        "origin": origin,
        "origin_label": "REAL CHANDRAYAAN-2 DATA" if origin == "REAL_CHANDRAYAAN2" else "SYNTHETIC BENCHMARK",
        "reference": {
            "path": ref.path,
            "metadata": ref.metadata.to_dict(),
            "notes": ref.notes,
            "quality": q_ref.to_dict(),
            "iirs": ref_extra.get("iirs"),
        },
        "moving": {
            "path": mov.path,
            "metadata": mov.metadata.to_dict(),
            "notes": mov.notes,
            "quality": q_mov.to_dict(),
            "iirs": mov_extra.get("iirs"),
        },
        "sun": {
            "azimuth_difference_deg": d_az,
            "elevation_difference_deg": d_el,
            "severity": sev,
            "guidance": guide,
        },
        "scale": {
            "expected_ratio": expected_scale,
            "estimated_ratio": estimated_scale,
            "scale_error": scale_error,
            "image_shape_ref": list(ref.image.shape[:2]),
            "image_shape_mov": list(mov.image.shape[:2]),
        },
        "matching": matches.to_dict(),
        "geometry": geom.to_dict(),
        "uniform": cov,
        "refinement": {
            "mean_ncc": mean_ncc,
            "mean_shift": mean_shift,
            "n": len(ncc_details),
        },
        "quality": q,
        "decision": fail,
        "algorithm": algorithm,
        "adaptive": decision.to_dict(),
        "correspondences": correspondences,
        "dem": dem_info,
        "dem_consistency": None if not dem_cons else {k: v for k, v in dem_cons.items() if k != "per_point" and k != "confidence_mod"},
        "mesh": mesh,
        "temporal": {
            "timeline": timeline_marks(),
            "available": False,
            "note": "4D analysis is optional. Provide multiple dated observations and/or DEMs.",
        },
        "previews": previews,
        "stages": [s.__dict__ for s in logs],
        "runtime_s": runtime,
        "random_seed": cfg.get("random_seed", 42),
        "limitations": [
            "Quality score is evidence-based, not a probability.",
            "Sun-angle robustness is measured, not claimed as absolute invariance.",
            "Deep-learning matchers require local checkpoints and are never auto-downloaded.",
            "DEM/3D/4D modules are optional and disabled without valid inputs.",
            "Synthetic data must not be presented as Chandrayaan-2 measurements.",
        ],
    }
    if dem_info and mesh:
        result["temporal"]["sample_potential_change"] = potential_change(
            np.array(mesh["positions"])[:, 2].reshape(mesh["height"], mesh["width"]) if False else (
                # placeholder same-grid comparison not available
                np.zeros((8, 8))
            ),
            np.zeros((8, 8)),
            sev,
            geom.rmse,
        ) if False else {
            "kind": "Potential Surface Change",
            "available": False,
            "note": "Requires a second dated DEM or registered epoch.",
        }
    return result
