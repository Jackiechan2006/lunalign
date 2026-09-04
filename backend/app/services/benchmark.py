from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np

from app.services.pipeline import run_registration
from core.synthetic.lunar import make_pair


def run_synthetic_benchmarks(out_root: str | Path, seed: int = 42) -> dict:
    """Software-pipeline benchmarks on labeled synthetic data. Not mission performance."""
    out_root = Path(out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    rows = []
    scales = [1.0, 2.0, 4.0]
    for scale in scales:
        pair = make_pair(seed=seed, scale=1.0 / scale if scale >= 1 else scale, rotation_deg=6.0)
        d = out_root / f"scale_{scale}"
        d.mkdir(exist_ok=True)
        ref_p = d / "ref.png"
        mov_p = d / "mov.png"
        cv2.imwrite(str(ref_p), (pair.reference * 255).astype(np.uint8))
        cv2.imwrite(str(mov_p), (pair.moving * 255).astype(np.uint8))
        t0 = time.perf_counter()
        res = run_registration(
            str(ref_p),
            str(mov_p),
            ref_sensor=pair.ref_meta["sensor"],
            mov_sensor=pair.mov_meta["sensor"],
            ref_meta=pair.ref_meta,
            mov_meta=pair.mov_meta,
            origin="SYNTHETIC_BENCHMARK",
            mode="classical",
            out_dir=d / "run",
        )
        rows.append(
            {
                "experiment": f"synthetic_scale_{scale}x",
                "origin": "SYNTHETIC BENCHMARK",
                "pair": "OHRC↔TMC (synthetic appearance)",
                "scale_factor": scale,
                "candidate_matches": res.get("matching", {}).get("raw_matches"),
                "final_matches": len(res.get("correspondences", [])),
                "inliers": res.get("geometry", {}).get("inliers"),
                "inlier_ratio": res.get("geometry", {}).get("inlier_ratio"),
                "rmse": res.get("geometry", {}).get("rmse"),
                "median_error": res.get("geometry", {}).get("median_error"),
                "p95_error": res.get("geometry", {}).get("p95_error"),
                "spatial_coverage": res.get("uniform", {}).get("coverage"),
                "grid_occupancy": res.get("uniform", {}).get("cells_occupied"),
                "scale_ratio": res.get("scale", {}).get("estimated_ratio"),
                "scale_error": res.get("scale", {}).get("scale_error"),
                "sun_az_diff": res.get("sun", {}).get("azimuth_difference_deg"),
                "sun_el_diff": res.get("sun", {}).get("elevation_difference_deg"),
                "ncc": res.get("refinement", {}).get("mean_ncc"),
                "subpixel_shift": res.get("refinement", {}).get("mean_shift"),
                "runtime_s": time.perf_counter() - t0,
                "quality_score": res.get("quality", {}).get("score"),
                "note": "Synthetic pipeline validation. Real mission data required for scientific validation.",
            }
        )
    return {
        "origin": "SYNTHETIC BENCHMARK",
        "disclaimer": "These metrics validate the software pipeline on generated imagery. They are not Chandrayaan-2 accuracy claims.",
        "algorithms_compared": ["SIFT/RootSIFT + RANSAC/USAC (LunaAlign classical)"],
        "missing": [
            "LoFTR — local checkpoint not auto-downloaded",
            "SuperPoint+SuperGlue — local checkpoint not auto-downloaded",
            "Real OHRC/TMC/IIRS pairs — Real mission data required for this validation.",
        ],
        "rows": rows,
    }
