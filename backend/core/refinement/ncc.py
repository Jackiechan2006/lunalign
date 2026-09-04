from __future__ import annotations

import numpy as np
from scipy.ndimage import map_coordinates


def extract_patch(image: np.ndarray, x: float, y: float, size: int) -> np.ndarray | None:
    half = size / 2.0
    yy, xx = np.mgrid[0:size, 0:size]
    xs = xx + (x - half)
    ys = yy + (y - half)
    h, w = image.shape[:2]
    if xs.min() < 0 or ys.min() < 0 or xs.max() >= w - 1 or ys.max() >= h - 1:
        return None
    patch = map_coordinates(image, [ys, xs], order=1, mode="nearest")
    return patch.astype(np.float32)


def ncc(a: np.ndarray, b: np.ndarray) -> float:
    a = a.ravel().astype(np.float64)
    b = b.ravel().astype(np.float64)
    a = a - a.mean()
    b = b - b.mean()
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom < 1e-9:
        return 0.0
    return float(np.dot(a, b) / denom)


def ncc_search(
    ref: np.ndarray,
    mov: np.ndarray,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    patch_size: int = 21,
    radius: int = 3,
) -> dict:
    """Local NCC peak + quadratic sub-pixel fit (classical CV)."""
    p_ref = extract_patch(ref, x1, y1, patch_size)
    if p_ref is None:
        return {
            "ok": False,
            "x": x2,
            "y": y2,
            "shift": 0.0,
            "ncc": None,
            "initial": [x2, y2],
        }
    best = -2.0
    bx, by = 0.0, 0.0
    grid = {}
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            p_m = extract_patch(mov, x2 + dx, y2 + dy, patch_size)
            if p_m is None:
                continue
            c = ncc(p_ref, p_m)
            grid[(dx, dy)] = c
            if c > best:
                best = c
                bx, by = float(dx), float(dy)
    # Quadratic peak along x and y independently if neighbors exist
    def quad(vm1, v0, vp1):
        denom = vm1 - 2 * v0 + vp1
        if abs(denom) < 1e-9:
            return 0.0
        return 0.5 * (vm1 - vp1) / denom

    ox = oy = 0.0
    if (int(bx) - 1, int(by)) in grid and (int(bx) + 1, int(by)) in grid:
        ox = quad(grid[(int(bx) - 1, int(by))], grid[(int(bx), int(by))], grid[(int(bx) + 1, int(by))])
    if (int(bx), int(by) - 1) in grid and (int(bx), int(by) + 1) in grid:
        oy = quad(grid[(int(bx), int(by) - 1)], grid[(int(bx), int(by))], grid[(int(bx), int(by) + 1)])
    rx, ry = x2 + bx + ox, y2 + by + oy
    shift = float(np.hypot(rx - x2, ry - y2))
    return {
        "ok": True,
        "x": rx,
        "y": ry,
        "shift": shift,
        "ncc": float(best),
        "initial": [x2, y2],
        "refined": [rx, ry],
    }


def refine_points(ref: np.ndarray, mov: np.ndarray, src: np.ndarray, dst: np.ndarray, **kw) -> tuple[np.ndarray, list[dict]]:
    refined = dst.copy().astype(np.float64)
    details = []
    for i, ((x1, y1), (x2, y2)) in enumerate(zip(src, dst)):
        d = ncc_search(ref, mov, float(x1), float(y1), float(x2), float(y2), **kw)
        details.append(d)
        if d["ok"]:
            refined[i] = [d["x"], d["y"]]
    return refined.astype(np.float32), details
