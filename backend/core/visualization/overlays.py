from __future__ import annotations

import cv2
import numpy as np

from core.preprocessing.normalize import to_uint8


def encode_png(image: np.ndarray) -> bytes:
    u8 = to_uint8(image)
    ok, buf = cv2.imencode(".png", u8)
    if not ok:
        raise RuntimeError("PNG encode failed")
    return buf.tobytes()


def overlay_warp(ref: np.ndarray, mov: np.ndarray, matrix: np.ndarray | None, model: str) -> np.ndarray:
    h, w = ref.shape[:2]
    r = to_uint8(ref)
    m = to_uint8(mov)
    if matrix is None:
        m2 = cv2.resize(m, (w, h))
    elif model == "homography" and matrix.shape == (3, 3):
        m2 = cv2.warpPerspective(m, matrix, (w, h))
    else:
        M = matrix[:2] if matrix.shape[0] == 3 else matrix
        m2 = cv2.warpAffine(m, M.astype(np.float32), (w, h))
    color = np.zeros((h, w, 3), dtype=np.uint8)
    color[..., 1] = r
    color[..., 2] = m2
    return color


def difference_map(ref: np.ndarray, mov: np.ndarray, matrix: np.ndarray | None, model: str) -> np.ndarray:
    h, w = ref.shape[:2]
    r = to_uint8(ref).astype(np.float32)
    m = to_uint8(mov)
    if matrix is None:
        m2 = cv2.resize(m, (w, h)).astype(np.float32)
    elif model == "homography" and matrix.shape == (3, 3):
        m2 = cv2.warpPerspective(m, matrix, (w, h)).astype(np.float32)
    else:
        M = matrix[:2] if matrix.shape[0] == 3 else matrix
        m2 = cv2.warpAffine(m, M.astype(np.float32), (w, h)).astype(np.float32)
    d = np.abs(r - m2)
    d = cv2.normalize(d, None, 0, 255, cv2.NORM_MINMAX)
    return d.astype(np.uint8)


def draw_matches(ref: np.ndarray, mov: np.ndarray, src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    r = to_uint8(ref)
    m = to_uint8(mov)
    h = max(r.shape[0], m.shape[0])
    w1, w2 = r.shape[1], m.shape[1]
    
    # Top banner height
    banner_h = 40
    canvas = np.zeros((h + banner_h, w1 + w2, 3), dtype=np.uint8)
    
    # Fill background
    canvas[:banner_h, :] = (20, 25, 35)
    canvas[banner_h : banner_h + r.shape[0], :w1, :] = cv2.cvtColor(r, cv2.COLOR_GRAY2BGR)
    canvas[banner_h : banner_h + m.shape[0], w1:, :] = cv2.cvtColor(m, cv2.COLOR_GRAY2BGR)
    
    # Header text
    cv2.putText(
        canvas,
        f"LUNAALIGN-X INLIER CORRESPONDENCE MAP  |  Points: {len(src)}",
        (15, 26),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 255, 200),
        2,
        cv2.LINE_AA,
    )
    
    offset = w1
    rng = np.random.default_rng(42)
    n = min(len(src), 300)
    for i in range(n):
        p1 = (int(src[i, 0]), int(src[i, 1]) + banner_h)
        p2 = (int(dst[i, 0]) + offset, int(dst[i, 1]) + banner_h)
        color = tuple(int(c) for c in rng.integers(100, 255, size=3))
        
        # Outer dark shadow line for contrast
        cv2.line(canvas, p1, p2, (0, 0, 0), 3, cv2.LINE_AA)
        # Inner colored line
        cv2.line(canvas, p1, p2, color, 1, cv2.LINE_AA)
        
        # Outer halo circle
        cv2.circle(canvas, p1, 4, (0, 0, 0), -1)
        cv2.circle(canvas, p2, 4, (0, 0, 0), -1)
        # Inner bright circle
        cv2.circle(canvas, p1, 2, color, -1)
        cv2.circle(canvas, p2, 2, color, -1)
        
    return canvas


def draw_inliers_high_vis(
    ref: np.ndarray,
    mov: np.ndarray,
    src_inliers: np.ndarray,
    dst_inliers: np.ndarray,
    src_candidates: np.ndarray | None = None,
    dst_candidates: np.ndarray | None = None,
    title: str = "RANSAC GEOMETRICALLY VERIFIED INLIERS",
    inlier_ratio: float | None = None,
    rmse: float | None = None,
) -> np.ndarray:
    r = to_uint8(ref)
    m = to_uint8(mov)
    h = max(r.shape[0], m.shape[0])
    w1, w2 = r.shape[1], m.shape[1]
    
    banner_h = 50
    canvas = np.zeros((h + banner_h, w1 + w2, 3), dtype=np.uint8)
    
    # Dark slate header bar
    canvas[:banner_h, :] = (15, 20, 28)
    canvas[banner_h : banner_h + r.shape[0], :w1, :] = cv2.cvtColor(r, cv2.COLOR_GRAY2BGR)
    canvas[banner_h : banner_h + m.shape[0], w1:, :] = cv2.cvtColor(m, cv2.COLOR_GRAY2BGR)
    
    # Image Labels on top left of each image
    cv2.putText(canvas, "REFERENCE (OHRC / Base)", (15, banner_h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(canvas, "MOVING (TMC-2 / Target)", (w1 + 15, banner_h + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
    
    # Banner title & stats
    stats_str = f"Inliers: {len(src_inliers)}"
    if src_candidates is not None:
        stats_str += f" / Total Matches: {len(src_candidates)}"
    if inlier_ratio is not None:
        stats_str += f" ({inlier_ratio*100:.1f}% Inliers)"
    if rmse is not None:
        stats_str += f" | RMSE: {rmse:.2f}px"
        
    cv2.putText(canvas, f"{title.upper()} — {stats_str}", (15, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 128), 2, cv2.LINE_AA)
    
    offset = w1
    
    # 1. Draw candidate matches (rejected outliers) in translucent dark cyan/gray if provided
    if src_candidates is not None and dst_candidates is not None:
        n_cand = min(len(src_candidates), 200)
        for i in range(n_cand):
            p1 = (int(src_candidates[i, 0]), int(src_candidates[i, 1]) + banner_h)
            p2 = (int(dst_candidates[i, 0]) + offset, int(dst_candidates[i, 1]) + banner_h)
            # Thin dim red/gray line for outliers
            cv2.line(canvas, p1, p2, (60, 60, 100), 1, cv2.LINE_AA)
            cv2.circle(canvas, p1, 2, (80, 80, 120), -1)
            cv2.circle(canvas, p2, 2, (80, 80, 120), -1)

    # 2. Draw verified RANSAC inliers in bold neon green with black outlines for maximum visibility
    n_in = len(src_inliers)
    for i in range(n_in):
        p1 = (int(src_inliers[i, 0]), int(src_inliers[i, 1]) + banner_h)
        p2 = (int(dst_inliers[i, 0]) + offset, int(dst_inliers[i, 1]) + banner_h)
        
        # Black outline line (thickness 3)
        cv2.line(canvas, p1, p2, (0, 0, 0), 3, cv2.LINE_AA)
        # Vibrant Neon Green vector (thickness 2)
        cv2.line(canvas, p1, p2, (0, 255, 128), 2, cv2.LINE_AA)
        
        # Outer black ring for keypoint
        cv2.circle(canvas, p1, 5, (0, 0, 0), -1)
        cv2.circle(canvas, p2, 5, (0, 0, 0), -1)
        # Inner vibrant neon green dot
        cv2.circle(canvas, p1, 3, (0, 255, 128), -1)
        cv2.circle(canvas, p2, 3, (0, 255, 128), -1)
        # Center white core dot
        cv2.circle(canvas, p1, 1, (255, 255, 255), -1)
        cv2.circle(canvas, p2, 1, (255, 255, 255), -1)
        
    return canvas


def draw_grid(image: np.ndarray, grid: tuple[int, int], pts: np.ndarray) -> np.ndarray:
    u8 = cv2.cvtColor(to_uint8(image), cv2.COLOR_GRAY2BGR)
    h, w = u8.shape[:2]
    gy, gx = grid
    
    banner_h = 40
    canvas = np.zeros((h + banner_h, w, 3), dtype=np.uint8)
    canvas[:banner_h, :] = (20, 25, 35)
    canvas[banner_h:, :] = u8
    
    cv2.putText(
        canvas,
        f"SPATIAL UNIFORMITY GRID ({gx}x{gy}) — Points: {len(pts)}",
        (15, 26),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 210, 255),
        2,
        cv2.LINE_AA,
    )
    
    for i in range(1, gx):
        x = int(i * w / gx)
        cv2.line(canvas, (x, banner_h), (x, h + banner_h), (40, 90, 140), 1)
    for j in range(1, gy):
        y = int(j * h / gy)
        cv2.line(canvas, (0, y + banner_h), (w, y + banner_h), (40, 90, 140), 1)
        
    for p in pts:
        pt = (int(p[0]), int(p[1]) + banner_h)
        cv2.circle(canvas, pt, 5, (0, 0, 0), -1)
        cv2.circle(canvas, pt, 3, (0, 210, 255), -1)
        cv2.circle(canvas, pt, 1, (255, 255, 255), -1)
        
    return canvas

