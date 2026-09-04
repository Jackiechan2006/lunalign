from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import cv2


@dataclass
class TransformResult:
    model: str
    matrix: Optional[np.ndarray]
    inlier_mask: Optional[np.ndarray]
    inliers: int
    candidates: int
    inlier_ratio: float
    rmse: Optional[float]
    median_error: Optional[float]
    p95_error: Optional[float]
    residuals: Optional[np.ndarray]
    method: str
    notes: list[str]

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "matrix": None if self.matrix is None else self.matrix.tolist(),
            "inliers": self.inliers,
            "candidates": self.candidates,
            "inlier_ratio": self.inlier_ratio,
            "rmse": self.rmse,
            "median_error": self.median_error,
            "p95_error": self.p95_error,
            "method": self.method,
            "notes": self.notes,
        }


def _method_flag() -> int:
    if hasattr(cv2, "USAC_MAGSAC"):
        return cv2.USAC_MAGSAC
    if hasattr(cv2, "USAC_DEFAULT"):
        return cv2.USAC_DEFAULT
    return cv2.RANSAC


def _reproj_errors(src: np.ndarray, dst: np.ndarray, matrix: np.ndarray, model: str) -> np.ndarray:
    src = src.reshape(-1, 2).astype(np.float64)
    dst = dst.reshape(-1, 2).astype(np.float64)
    if model == "homography":
        pred = cv2.perspectiveTransform(src.reshape(-1, 1, 2), matrix).reshape(-1, 2)
    else:
        pred = cv2.transform(src.reshape(-1, 1, 2), matrix[:2]).reshape(-1, 2)
    return np.linalg.norm(pred - dst, axis=1)


def _fit(model: str, src: np.ndarray, dst: np.ndarray, thresh: float, max_iters: int, conf: float):
    method = _method_flag()
    method_name = "USAC/MAGSAC" if method != cv2.RANSAC else "RANSAC"
    src32 = src.reshape(-1, 1, 2).astype(np.float32)
    dst32 = dst.reshape(-1, 1, 2).astype(np.float32)
    if model == "translation":
        # Statistical robust location of displacement (not ML).
        delta = dst.reshape(-1, 2) - src.reshape(-1, 2)
        med = np.median(delta, axis=0)
        err = np.linalg.norm(delta - med, axis=1)
        mask = err <= thresh
        M = np.array([[1, 0, med[0]], [0, 1, med[1]]], dtype=np.float64)
        return M, mask.astype(np.uint8), method_name
    if model == "similarity":
        aff_method = method if method in (cv2.RANSAC, cv2.LMEDS) else cv2.RANSAC
        M, mask = cv2.estimateAffinePartial2D(
            src32, dst32, method=aff_method, ransacReprojThreshold=thresh,
            maxIters=max_iters, confidence=conf,
        )
        return M, mask, "USAC/MAGSAC" if method != cv2.RANSAC else "RANSAC"
    if model == "affine":
        aff_method = method if method in (cv2.RANSAC, cv2.LMEDS) else cv2.RANSAC
        M, mask = cv2.estimateAffine2D(
            src32, dst32, method=aff_method, ransacReprojThreshold=thresh,
            maxIters=max_iters, confidence=conf,
        )
        return M, mask, "USAC/MAGSAC" if method != cv2.RANSAC else "RANSAC"
    M, mask = cv2.findHomography(
        src32, dst32, method=method, ransacReprojThreshold=thresh,
        maxIters=max_iters, confidence=conf,
    )
    return M, mask, method_name


def select_model(n: int, scale_ratio: Optional[float], same_sensor: bool) -> list[str]:
    """Choose candidate geometric models from data characteristics."""
    if n < 8:
        return ["translation", "similarity"]
    if scale_ratio is not None and abs(np.log2(max(scale_ratio, 1e-6))) > 0.4:
        return ["similarity", "affine"]
    if not same_sensor:
        return ["affine", "homography", "similarity"]
    return ["similarity", "affine", "homography"]


def estimate_transform(
    src_pts: np.ndarray,
    dst_pts: np.ndarray,
    model: str = "affine",
    thresh: float = 3.0,
    max_iters: int = 2000,
    confidence: float = 0.999,
) -> TransformResult:
    notes = [
        "RANSAC/USAC/MAGSAC is robust geometric/statistical estimation, not machine learning.",
    ]
    n = len(src_pts)
    if n < 3:
        return TransformResult(
            model=model, matrix=None, inlier_mask=None, inliers=0, candidates=n,
            inlier_ratio=0.0, rmse=None, median_error=None, p95_error=None,
            residuals=None, method="none", notes=notes + ["Too few points."],
        )
    M, mask, method_name = _fit(model, src_pts, dst_pts, thresh, max_iters, confidence)
    if M is None or mask is None:
        return TransformResult(
            model=model, matrix=None, inlier_mask=None, inliers=0, candidates=n,
            inlier_ratio=0.0, rmse=None, median_error=None, p95_error=None,
            residuals=None, method=method_name, notes=notes + ["Estimator failed."],
        )
    mask_b = mask.ravel().astype(bool)
    inliers = int(mask_b.sum())
    residuals = _reproj_errors(src_pts, dst_pts, M, model)
    inlier_res = residuals[mask_b] if inliers else residuals
    rmse = float(np.sqrt(np.mean(inlier_res ** 2))) if inlier_res.size else None
    med = float(np.median(inlier_res)) if inlier_res.size else None
    p95 = float(np.percentile(inlier_res, 95)) if inlier_res.size else None
    return TransformResult(
        model=model,
        matrix=M,
        inlier_mask=mask_b,
        inliers=inliers,
        candidates=n,
        inlier_ratio=inliers / max(n, 1),
        rmse=rmse,
        median_error=med,
        p95_error=p95,
        residuals=residuals,
        method=method_name,
        notes=notes,
    )


def auto_estimate(
    src_pts: np.ndarray,
    dst_pts: np.ndarray,
    scale_ratio: Optional[float],
    same_sensor: bool,
    thresh: float = 3.0,
) -> TransformResult:
    best: TransformResult | None = None
    for model in select_model(len(src_pts), scale_ratio, same_sensor):
        r = estimate_transform(src_pts, dst_pts, model=model, thresh=thresh)
        score = -1e9
        if r.matrix is not None and r.rmse is not None:
            score = r.inlier_ratio * 2.0 - min(r.rmse, 20.0) / 10.0
        if best is None or score > (
            best.inlier_ratio * 2.0 - min(best.rmse or 20.0, 20.0) / 10.0
        ):
            best = r
    assert best is not None
    return best
