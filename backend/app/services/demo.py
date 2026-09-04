from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from app.services.pipeline import run_registration
from core.synthetic.lunar import make_pair


DEMO_STEPS = [
    {"id": "problem", "title": "PROBLEM", "body": "Multi-modal, sun-angle and scale invariant correspondence for Chandrayaan-2 OHRC, TMC-2 and IIRS."},
    {"id": "pair", "title": "OHRC vs TMC", "body": "Different spatial resolution, different illumination, different appearance."},
    {"id": "preprocess", "title": "LunaAlign-X preprocessing", "body": "CLAHE, local contrast normalization, gradients and multi-scale pyramids. Illumination-robust representations, not claimed invariance."},
    {"id": "features", "title": "Feature extraction", "body": "Classical computer vision: SIFT keypoints with RootSIFT descriptors (L1 + sqrt)."},
    {"id": "match", "title": "Correspondence", "body": "BF KNN matching, Lowe ratio test, optional mutual nearest neighbors."},
    {"id": "ransac", "title": "Geometric verification", "body": "RANSAC/USAC/MAGSAC is robust geometric/statistical estimation, not machine learning."},
    {"id": "uniform", "title": "Uniform matches", "body": "8×8 grid selection prevents clustering in a single crater."},
    {"id": "subpixel", "title": "Sub-pixel refinement", "body": "Local NCC + quadratic peak fitting."},
    {"id": "metrics", "title": "Metrics", "body": "Inlier ratio, RMSE, coverage and an evidence-based quality score (not a probability)."},
    {"id": "dem", "title": "DEM-assisted verification", "body": "Optional. If no real DEM is supplied, 2D registration still completes."},
    {"id": "viz3d", "title": "3D visualization", "body": "Optional textured DEM viewer. Secondary to correspondence."},
    {"id": "viz4d", "title": "Optional 4D extension", "body": "X,Y,Z,T potential surface change — never auto-confirmed as physical change."},
]


def build_demo_pair(out_dir: Path) -> tuple[str, str, dict, dict]:
    pair = make_pair(seed=7, scale=0.72, rotation_deg=7.5, tx=14, ty=-11)
    out_dir.mkdir(parents=True, exist_ok=True)
    ref_p = out_dir / "demo_ref.png"
    mov_p = out_dir / "demo_mov.png"
    cv2.imwrite(str(ref_p), (np.clip(pair.reference, 0, 1) * 255).astype(np.uint8))
    cv2.imwrite(str(mov_p), (np.clip(pair.moving, 0, 1) * 255).astype(np.uint8))
    return str(ref_p), str(mov_p), pair.ref_meta, pair.mov_meta


def run_sih_demo(out_dir: str | Path) -> dict:
    out_dir = Path(out_dir)
    ref_p, mov_p, rm, mm = build_demo_pair(out_dir / "inputs")
    result = run_registration(
        ref_p,
        mov_p,
        ref_sensor="OHRC",
        mov_sensor="TMC",
        ref_meta=rm,
        mov_meta=mm,
        origin="SYNTHETIC_BENCHMARK",
        mode="automatic",
        allow_synthetic_dem=True,
        out_dir=out_dir / "run",
    )
    result["demo_steps"] = DEMO_STEPS
    result["demo_story"] = (
        "This SIH demonstration uses a synthetic crater field with a known similarity "
        "transform so every displayed metric is computed by the real pipeline. "
        "Real mission data required for scientific validation of Chandrayaan-2 products."
    )
    return result
