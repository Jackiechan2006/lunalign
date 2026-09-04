from __future__ import annotations

import numpy as np


def select_uniform(
    src_pts: np.ndarray,
    dst_pts: np.ndarray,
    scores: np.ndarray,
    image_shape: tuple[int, int],
    grid: tuple[int, int] = (8, 8),
    max_per_cell: int = 8,
    min_separation: float = 8.0,
) -> tuple[np.ndarray, dict]:
    """Spatially diverse correspondences via grid ranking + NMS. Not random matching."""
    h, w = image_shape[:2]
    gy, gx = grid
    if len(src_pts) == 0:
        stats = {
            "grid": [gy, gx],
            "cells_occupied": 0,
            "coverage": 0.0,
            "points_per_cell": 0.0,
            "min_separation": min_separation,
            "n_selected": 0,
        }
        return np.zeros(0, dtype=int), stats

    xs = np.clip((src_pts[:, 0] / max(w, 1)) * gx, 0, gx - 1e-6).astype(int)
    ys = np.clip((src_pts[:, 1] / max(h, 1)) * gy, 0, gy - 1e-6).astype(int)
    cells = ys * gx + xs
    selected: list[int] = []
    occupied = set()
    for cell in np.unique(cells):
        idx = np.where(cells == cell)[0]
        order = idx[np.argsort(-scores[idx])]
        kept_cell: list[int] = []
        for i in order:
            if len(kept_cell) >= max_per_cell:
                break
            p = src_pts[i]
            if kept_cell:
                d = np.linalg.norm(src_pts[kept_cell] - p, axis=1)
                if np.min(d) < min_separation:
                    continue
            if selected:
                d2 = np.linalg.norm(src_pts[selected] - p, axis=1)
                if np.min(d2) < min_separation * 0.5:
                    continue
            kept_cell.append(int(i))
        if kept_cell:
            occupied.add(int(cell))
            selected.extend(kept_cell)
    sel = np.array(selected, dtype=int)
    n_cells = gy * gx
    stats = {
        "grid": [gy, gx],
        "cells_occupied": len(occupied),
        "coverage": len(occupied) / n_cells,
        "points_per_cell": float(len(sel) / max(len(occupied), 1)),
        "min_separation": min_separation,
        "n_selected": int(len(sel)),
    }
    return sel, stats
