from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from core.preprocessing.normalize import (
    clahe,
    edge_map,
    gaussian_pyramid,
    local_contrast_normalize,
    percentile_stretch,
    phase_congruency_proxy,
    replace_invalid,
    gradients,
)


@dataclass
class Representations:
    intensity: np.ndarray
    clahe: np.ndarray
    lcn: np.ndarray
    gradient_mag: np.ndarray
    gradient_ori: np.ndarray
    edges: np.ndarray
    phase_proxy: np.ndarray
    pyramid: list[np.ndarray]
    matching_image: np.ndarray
    extras: dict[str, Any] = field(default_factory=dict)


def preprocess_ohrc(image: np.ndarray) -> Representations:
    """OHRC: invalid pixels → stretch → CLAHE → LCN → gradients → multi-scale."""
    clean = replace_invalid(image)
    intensity = percentile_stretch(clean)
    cl = clahe(intensity)
    lcn = local_contrast_normalize(intensity)
    mag, ori, *_ = gradients(cl)
    edges = edge_map(cl)
    phase = phase_congruency_proxy(cl)
    pyr = gaussian_pyramid(cl, levels=4)
    matching = 0.45 * cl + 0.35 * mag + 0.20 * np.abs(lcn) / (np.abs(lcn).max() + 1e-6)
    matching = np.clip(matching, 0, 1).astype(np.float32)
    return Representations(
        intensity=intensity,
        clahe=cl,
        lcn=lcn,
        gradient_mag=mag,
        gradient_ori=ori,
        edges=edges,
        phase_proxy=phase,
        pyramid=pyr,
        matching_image=matching,
        extras={"pipeline": "OHRC"},
    )


def preprocess_tmc(image: np.ndarray) -> Representations:
    """TMC: similar illumination-robust path; retains lower GSD characteristics."""
    reps = preprocess_ohrc(image)
    reps.extras["pipeline"] = "TMC"
    return reps
