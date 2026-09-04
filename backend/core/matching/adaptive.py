from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.preprocessing.normalize import percentile_stretch


def _texture_score(image: np.ndarray) -> float:
    img = percentile_stretch(image)
    gy, gx = np.gradient(img)
    mag = np.sqrt(gx * gx + gy * gy)
    return float(np.mean(mag))


def _contrast_score(image: np.ndarray) -> float:
    img = percentile_stretch(image)
    return float(img.std())


@dataclass
class AdaptiveDecision:
    family: str  # Classical | Deep Learning | Hybrid
    matcher: str
    reasons: list[str]
    features: dict

    def to_dict(self) -> dict:
        return {
            "family": self.family,
            "matcher": self.matcher,
            "reasons": self.reasons,
            "features": self.features,
        }


def decide(
    *,
    ref_image: np.ndarray,
    mov_image: np.ndarray,
    ref_sensor: str,
    mov_sensor: str,
    scale_ratio: float | None,
    sun_severity: str,
    mode: str,
    deep_available: bool,
    n_features_hint: int | None = None,
) -> AdaptiveDecision:
    texture = 0.5 * (_texture_score(ref_image) + _texture_score(mov_image))
    contrast = 0.5 * (_contrast_score(ref_image) + _contrast_score(mov_image))
    same = ref_sensor == mov_sensor
    scale = scale_ratio if scale_ratio else 1.0
    log_scale = abs(np.log2(max(scale, 1e-6)))
    feats = {
        "texture": texture,
        "contrast": contrast,
        "scale_ratio": scale,
        "sun_severity": sun_severity,
        "same_sensor": same,
        "ref_sensor": ref_sensor,
        "mov_sensor": mov_sensor,
        "deep_available": deep_available,
    }
    reasons: list[str] = []

    if mode == "classical":
        reasons.append("User selected classical computer vision.")
        matcher = "SIFT-multiscale/RootSIFT" if log_scale > 0.5 else "SIFT/RootSIFT"
        return AdaptiveDecision("Classical Computer Vision", matcher, reasons, feats)
    if mode == "deep":
        if deep_available:
            reasons.append("User selected deep-learning correspondence.")
            return AdaptiveDecision("Deep Learning", "LoFTR", reasons, feats)
        reasons.append("Deep matcher unavailable. Classical fallback.")
        return AdaptiveDecision("Classical Computer Vision", "SIFT/RootSIFT", reasons, feats)
    if mode == "hybrid":
        if deep_available:
            reasons.append("User selected hybrid classical + deep-learning correspondence.")
            return AdaptiveDecision("Hybrid", "RootSIFT+LoFTR", reasons, feats)
        reasons.append("Hybrid requested but ML weights missing. Classical fallback.")
        return AdaptiveDecision("Classical Computer Vision", "SIFT/RootSIFT", reasons, feats)

    # automatic
    if not same:
        reasons.append("Cross-modal pair (different sensors).")
        if deep_available:
            reasons.append("LoFTR selected if available for appearance-divergent modalities.")
            return AdaptiveDecision("Hybrid", "RootSIFT+LoFTR", reasons, feats)
        reasons.append("ML unavailable → multi-scale RootSIFT on illumination-robust representations.")
        return AdaptiveDecision("Classical Computer Vision", "SIFT-multiscale/RootSIFT", reasons, feats)
    if log_scale > 0.8:
        reasons.append("Large scale/GSD difference → multi-scale SIFT.")
        return AdaptiveDecision("Classical Computer Vision", "SIFT-multiscale/RootSIFT", reasons, feats)
    if texture > 0.04 and same:
        reasons.append("Same sensor + sufficient texture → SIFT/RootSIFT.")
        return AdaptiveDecision("Classical Computer Vision", "SIFT/RootSIFT", reasons, feats)
    if sun_severity == "large":
        reasons.append("Large sun-angle difference → gradient-domain RootSIFT.")
        return AdaptiveDecision("Classical Computer Vision", "SIFT/RootSIFT", reasons, feats)
    reasons.append("Default automatic policy: classical RootSIFT.")
    return AdaptiveDecision("Classical Computer Vision", "SIFT/RootSIFT", reasons, feats)
