from __future__ import annotations

from typing import Any, Optional


def _clip01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))


def quality_score(
    *,
    inlier_ratio: float,
    rmse: Optional[float],
    median_error: Optional[float],
    coverage: float,
    mean_ncc: Optional[float],
    mean_ratio: Optional[float],
    subpixel_shift: Optional[float],
    dem_residual: Optional[float],
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Evidence-based registration quality score in [0, 1]. Not a probability."""
    w = weights or {
        "inlier_ratio": 0.22,
        "rmse": 0.18,
        "median_error": 0.10,
        "coverage": 0.16,
        "ncc": 0.14,
        "descriptor": 0.08,
        "stability": 0.06,
        "subpixel": 0.06,
    }
    parts = {}
    parts["inlier_ratio"] = _clip01(inlier_ratio)
    parts["rmse"] = _clip01(0 if rmse is None else 1.0 - min(rmse, 10.0) / 10.0)
    parts["median_error"] = _clip01(
        0 if median_error is None else 1.0 - min(median_error, 8.0) / 8.0
    )
    parts["coverage"] = _clip01(coverage)
    parts["ncc"] = _clip01(0.0 if mean_ncc is None else (mean_ncc + 1.0) / 2.0)
    parts["descriptor"] = _clip01(0.0 if mean_ratio is None else 1.0 - mean_ratio)
    parts["subpixel"] = _clip01(
        0.5 if subpixel_shift is None else 1.0 - min(subpixel_shift, 4.0) / 4.0
    )
    if dem_residual is None:
        parts["stability"] = 0.5
    else:
        parts["stability"] = _clip01(1.0 - min(dem_residual, 50.0) / 50.0)

    score = 0.0
    wsum = 0.0
    for k, wt in w.items():
        if k in parts:
            score += wt * parts[k]
            wsum += wt
    score = score / wsum if wsum else 0.0
    if score >= 0.75:
        band = "HIGH"
    elif score >= 0.5:
        band = "MEDIUM"
    else:
        band = "LOW"
    return {
        "score": round(float(score), 4),
        "band": band,
        "components": parts,
        "disclaimer": (
            "Evidence-based registration quality score (0–1), not a probability "
            "of correctness. Combines geometric residuals, inlier ratio, coverage, NCC, "
            "and optional DEM consistency."
        ),
    }


def failure_flags(
    *,
    n_matches: int,
    inlier_ratio: float,
    rmse: Optional[float],
    coverage: float,
    mean_ncc: Optional[float],
    cfg: dict | None = None,
) -> dict[str, Any]:
    c = cfg or {}
    reasons = []
    if n_matches < int(c.get("min_inliers", 12)):
        reasons.append("Too few geometrically consistent matches.")
    if inlier_ratio < float(c.get("min_inlier_ratio", 0.25)):
        reasons.append("Low inlier ratio.")
    if rmse is not None and rmse > float(c.get("max_rmse_px", 4.0)):
        reasons.append("High RMSE.")
    if coverage < float(c.get("min_coverage", 0.35)):
        reasons.append("Poor spatial coverage.")
    if mean_ncc is not None and mean_ncc < 0.25:
        reasons.append("Poor NCC after refinement.")
    accepted = len(reasons) == 0
    return {
        "accepted": accepted,
        "status": "REGISTRATION ACCEPTED" if accepted else "REGISTRATION REQUIRES REVIEW",
        "reasons": reasons,
    }
