from __future__ import annotations

import numpy as np
import cv2


def replace_invalid(image: np.ndarray, fill: str = "median") -> np.ndarray:
    img = image.astype(np.float32).copy()
    mask = ~np.isfinite(img)
    if not mask.any():
        return img
    finite = img[~mask]
    value = float(np.median(finite)) if finite.size and fill == "median" else 0.0
    img[mask] = value
    return img


def percentile_stretch(image: np.ndarray, p_low: float = 1.0, p_high: float = 99.0) -> np.ndarray:
    img = replace_invalid(image)
    lo, hi = np.percentile(img, [p_low, p_high])
    if hi <= lo:
        return np.zeros_like(img, dtype=np.float32)
    return np.clip((img - lo) / (hi - lo), 0, 1).astype(np.float32)


def to_uint8(image: np.ndarray) -> np.ndarray:
    if image.dtype == np.uint8:
        return image
    stretched = percentile_stretch(image)
    return (stretched * 255.0).astype(np.uint8)


def clahe(image: np.ndarray, clip: float = 2.0, grid: int = 8) -> np.ndarray:
    u8 = to_uint8(image)
    eq = cv2.createCLAHE(clipLimit=clip, tileGridSize=(grid, grid))
    out = eq.apply(u8)
    return out.astype(np.float32) / 255.0


def local_contrast_normalize(image: np.ndarray, ksize: int = 9, eps: float = 1e-6) -> np.ndarray:
    img = percentile_stretch(image)
    mean = cv2.GaussianBlur(img, (ksize, ksize), 0)
    sq = cv2.GaussianBlur(img * img, (ksize, ksize), 0)
    var = np.clip(sq - mean * mean, 0, None)
    return ((img - mean) / (np.sqrt(var) + eps)).astype(np.float32)


def gradients(image: np.ndarray):
    img = percentile_stretch(image)
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx * gx + gy * gy)
    ori = np.arctan2(gy, gx)
    if mag.max() > 0:
        mag = mag / mag.max()
    return mag.astype(np.float32), ori.astype(np.float32), gx, gy


def edge_map(image: np.ndarray) -> np.ndarray:
    u8 = to_uint8(image)
    return (cv2.Canny(u8, 60, 160).astype(np.float32) / 255.0)


def gaussian_pyramid(image: np.ndarray, levels: int = 4) -> list[np.ndarray]:
    img = percentile_stretch(image)
    pyr = [img]
    cur = img
    for _ in range(levels - 1):
        cur = cv2.pyrDown(cur)
        pyr.append(cur)
    return pyr


def phase_congruency_proxy(image: np.ndarray) -> np.ndarray:
    """Log-Gabor inspired high-pass phase proxy (classical CV, not ML)."""
    img = percentile_stretch(image)
    blur = cv2.GaussianBlur(img, (0, 0), 2.0)
    hip = img - blur
    mag, _, _, _ = gradients(hip)  # type: ignore[misc]
    return mag
