from __future__ import annotations

import numpy as np

from core.matching.knn import MatchSet


def fuse_matches(classical: MatchSet, deep: MatchSet | None, dup_px: float = 3.0) -> MatchSet:
    """Union of classical and deep correspondences in a common coordinate frame."""
    if deep is None or len(deep.src_pts) == 0:
        return classical
    if len(classical.src_pts) == 0:
        return deep
    src = [classical.src_pts, deep.src_pts]
    dst = [classical.dst_pts, deep.dst_pts]
    dist = [classical.distances, deep.distances]
    ratio = [classical.ratios, deep.ratios]
    S = np.vstack(src)
    D = np.vstack(dst)
    keep = np.ones(len(S), dtype=bool)
    for i in range(len(S)):
        if not keep[i]:
            continue
        d = np.linalg.norm(S[i + 1 :] - S[i], axis=1)
        e = np.linalg.norm(D[i + 1 :] - D[i], axis=1)
        dup = (d < dup_px) & (e < dup_px)
        keep[i + 1 :][dup] = False
    S, D = S[keep], D[keep]
    distances = np.concatenate(dist)[keep]
    ratios = np.concatenate(ratio)[keep]
    n = len(S)
    return MatchSet(
        src_idx=np.arange(n),
        dst_idx=np.arange(n),
        src_pts=S.astype(np.float32),
        dst_pts=D.astype(np.float32),
        distances=distances.astype(np.float32),
        ratios=ratios.astype(np.float32),
        raw_count=classical.raw_count + deep.raw_count,
        ratio_count=classical.ratio_count + deep.ratio_count,
        mutual_count=n,
        matcher=f"hybrid:{classical.matcher}+{deep.matcher}",
    )
