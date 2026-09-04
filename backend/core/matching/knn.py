from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class MatchSet:
    src_idx: np.ndarray
    dst_idx: np.ndarray
    src_pts: np.ndarray
    dst_pts: np.ndarray
    distances: np.ndarray
    ratios: np.ndarray
    raw_count: int
    ratio_count: int
    mutual_count: int
    matcher: str

    def to_dict(self) -> dict:
        return {
            "raw_matches": self.raw_count,
            "ratio_test_matches": self.ratio_count,
            "mutual_matches": self.mutual_count,
            "matcher": self.matcher,
            "n": int(len(self.src_pts)),
        }


def knn_match(
    desc1: np.ndarray,
    desc2: np.ndarray,
    pts1: np.ndarray,
    pts2: np.ndarray,
    ratio: float = 0.75,
    mutual: bool = True,
    use_flann: bool = False,
) -> MatchSet:
    if desc1 is None or desc2 is None or len(desc1) < 2 or len(desc2) < 2:
        return MatchSet(
            np.zeros(0, dtype=int), np.zeros(0, dtype=int),
            np.zeros((0, 2)), np.zeros((0, 2)), np.zeros(0), np.zeros(0),
            0, 0, 0, "none",
        )
    d1 = desc1.astype(np.float32)
    d2 = desc2.astype(np.float32)
    if use_flann:
        index_params = dict(algorithm=1, trees=5)
        search_params = dict(checks=50)
        matcher = cv2.FlannBasedMatcher(index_params, search_params)
        name = "FLANN KNN"
    else:
        matcher = cv2.BFMatcher(cv2.NORM_L2)
        name = "BF KNN"
    raw = matcher.knnMatch(d1, d2, k=2)
    raw_count = len(raw)
    good = []
    ratios = []
    for pair in raw:
        if len(pair) < 2:
            continue
        m, n = pair
        r = m.distance / (n.distance + 1e-8)
        if r < ratio:
            good.append(m)
            ratios.append(r)
    ratio_count = len(good)
    if mutual and good:
        back = matcher.knnMatch(d2, d1, k=1)
        nn_back = {m.queryIdx: m.trainIdx for (m,) in back if m is not None}
        kept = []
        kept_r = []
        for m, r in zip(good, ratios):
            if nn_back.get(m.trainIdx) == m.queryIdx:
                kept.append(m)
                kept_r.append(r)
        good, ratios = kept, kept_r
    mutual_count = len(good) if mutual else ratio_count
    if not good:
        return MatchSet(
            np.zeros(0, dtype=int), np.zeros(0, dtype=int),
            np.zeros((0, 2)), np.zeros((0, 2)), np.zeros(0), np.zeros(0),
            raw_count, ratio_count, 0, name,
        )
    src_idx = np.array([m.queryIdx for m in good], dtype=int)
    dst_idx = np.array([m.trainIdx for m in good], dtype=int)
    return MatchSet(
        src_idx=src_idx,
        dst_idx=dst_idx,
        src_pts=pts1[src_idx],
        dst_pts=pts2[dst_idx],
        distances=np.array([m.distance for m in good], dtype=np.float32),
        ratios=np.array(ratios, dtype=np.float32),
        raw_count=raw_count,
        ratio_count=ratio_count,
        mutual_count=mutual_count,
        matcher=name,
    )
