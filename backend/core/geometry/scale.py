from __future__ import annotations

from typing import Optional

import numpy as np
import cv2


def gsd_scale_ratio(ref_gsd: Optional[float], mov_gsd: Optional[float]) -> Optional[float]:
    if not ref_gsd or not mov_gsd or ref_gsd <= 0 or mov_gsd <= 0:
        return None
    return float(mov_gsd / ref_gsd)


def image_shape_ratio(ref_shape, mov_shape) -> float:
    return float(np.sqrt((mov_shape[0] * mov_shape[1]) / (ref_shape[0] * ref_shape[1] + 1e-9)))


def estimate_scale_from_transform(matrix: np.ndarray, model: str) -> Optional[float]:
    if matrix is None:
        return None
    m = np.asarray(matrix, dtype=np.float64)
    if model == "translation":
        return 1.0
    if m.shape == (2, 3) or m.shape == (3, 3):
        a, b = m[0, 0], m[0, 1]
        c, d = m[1, 0], m[1, 1]
        sx = np.sqrt(a * a + c * c)
        sy = np.sqrt(b * b + d * d)
        return float(0.5 * (sx + sy))
    return None


def phase_correlation_shift(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    """Classical Fourier phase correlation (not ML)."""
    a8 = cv2.normalize(a, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    b8 = cv2.normalize(b, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    shift, response = cv2.phaseCorrelate(
        np.float32(a8), np.float32(b8)
    )
    return float(shift[0]), float(shift[1]), float(response)
