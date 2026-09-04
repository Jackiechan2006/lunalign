from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import numpy as np


@dataclass
class Epoch:
    t: str
    label: str
    z: Optional[np.ndarray]
    image_id: Optional[str] = None


def parse_time(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d"):
        try:
            return datetime.strptime(value[:19], fmt)
        except ValueError:
            continue
    return None


def potential_change(
    z1: np.ndarray,
    z2: np.ndarray,
    sun_severity: str,
    rmse_px: Optional[float],
) -> dict:
    """Compare two elevation rasters. Do not claim confirmed physical change."""
    a = z1.astype(np.float32)
    b = z2.astype(np.float32)
    if a.shape != b.shape:
        ys = min(a.shape[0], b.shape[0])
        xs = min(a.shape[1], b.shape[1])
        a, b = a[:ys, :xs], b[:ys, :xs]
    dz = b - a
    confounders = [
        "illumination / sun angle",
        "viewing geometry",
        "sensor differences",
        "registration error",
        "noise",
    ]
    if sun_severity in {"large", "moderate", "unknown"}:
        confounders.append("sun-angle difference between epochs")
    if rmse_px is not None:
        confounders.append(f"2D registration RMSE ≈ {rmse_px:.2f} px")
    mag = np.abs(dz)
    p95 = float(np.nanpercentile(mag, 95)) if mag.size else 0.0
    conf = "low"
    if sun_severity == "small" and (rmse_px is None or rmse_px < 1.5):
        conf = "medium"
    return {
        "kind": "Potential Surface Change",
        "not": "Confirmed Surface Change",
        "mean_dz": float(np.nanmean(dz)),
        "p95_abs_dz": p95,
        "difference_preview": _preview(dz),
        "confidence": conf,
        "confounders": confounders,
        "disclaimer": (
            "Image or DEM differences are potential surface change only. "
            "They are not confirmed physical lunar surface change without independent validation."
        ),
    }


def _preview(dz: np.ndarray, size: int = 64) -> list:
    h, w = dz.shape
    step_y = max(h // size, 1)
    step_x = max(w // size, 1)
    small = dz[::step_y, ::step_x]
    finite = small[np.isfinite(small)]
    if finite.size == 0:
        return small.tolist()
    lim = float(np.percentile(np.abs(finite), 98) + 1e-6)
    n = np.clip(small / lim, -1, 1)
    return n.round(3).tolist()


def timeline_marks(years: list[int] | None = None) -> list[int]:
    return years or [2010, 2012, 2016, 2020, 2024]
