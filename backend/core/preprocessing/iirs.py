from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
from sklearn.decomposition import PCA

from core.preprocessing.normalize import percentile_stretch, gradients, replace_invalid
from core.preprocessing.optical import Representations, preprocess_ohrc


@dataclass
class IIRSResult:
    representations: Representations
    explained_variance: list[float]
    retained_variance: float
    n_components: int
    valid_bands: int
    total_bands: int
    pc_maps: list[np.ndarray] = field(default_factory=list)
    pca_composite: Optional[np.ndarray] = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "explained_variance": self.explained_variance,
            "retained_variance": self.retained_variance,
            "n_components": self.n_components,
            "valid_bands": self.valid_bands,
            "total_bands": self.total_bands,
            "notes": self.notes,
        }


def _valid_band_mask(cube: np.ndarray) -> np.ndarray:
    band_ok = []
    for b in range(cube.shape[2]):
        sl = cube[..., b]
        finite = np.isfinite(sl)
        if finite.mean() < 0.5:
            band_ok.append(False)
            continue
        vals = sl[finite]
        band_ok.append(float(vals.std()) > 1e-8)
    return np.array(band_ok, dtype=bool)


def preprocess_iirs(cube_or_image: np.ndarray, n_components: int = 3) -> IIRSResult:
    """IIRS is treated as X×Y×bands. PCA is dimensionality reduction, not deep learning."""
    notes: list[str] = []
    if cube_or_image.ndim == 2:
        notes.append("Single-band IIRS-like array: PCA skipped; optical pipeline used.")
        reps = preprocess_ohrc(cube_or_image)
        reps.extras["pipeline"] = "IIRS-fallback-2D"
        return IIRSResult(reps, [], 0.0, 0, 1, 1, notes=notes)

    cube = cube_or_image.astype(np.float32)
    h, w, b = cube.shape
    mask = _valid_band_mask(cube)
    valid = cube[..., mask]
    if valid.shape[2] < 2:
        notes.append("IIRS data detected but spectral bands are invalid or insufficient.")
        fallback = np.nanmean(replace_invalid(np.nan_to_num(cube, nan=np.nan)), axis=2)
        reps = preprocess_ohrc(fallback)
        return IIRSResult(reps, [], 0.0, 0, int(mask.sum()), b, notes=notes)

    k = int(np.clip(n_components, 2, min(10, valid.shape[2])))
    x = valid.reshape(-1, valid.shape[2])
    finite = np.isfinite(x).all(axis=1)
    x2 = x.copy()
    if (~finite).any():
        med = np.nanmedian(x[finite], axis=0)
        x2[~finite] = med
    # Spectral L2 normalization per pixel
    norms = np.linalg.norm(x2, axis=1, keepdims=True) + 1e-8
    x2 = x2 / norms
    pca = PCA(n_components=k, random_state=42)
    z = pca.fit_transform(x2)
    ev = pca.explained_variance_ratio_.tolist()
    pcs = [z[:, i].reshape(h, w).astype(np.float32) for i in range(k)]
    # RGB-like composite from first 3 PCs (or fewer)
    chans = []
    for i in range(min(3, k)):
        chans.append(percentile_stretch(pcs[i]))
    while len(chans) < 3:
        chans.append(chans[-1])
    composite = np.stack(chans, axis=-1)
    matching_base = pcs[0]
    mag, ori, *_ = gradients(matching_base)
    spectral_grad = mag
    reps = preprocess_ohrc(matching_base)
    reps.gradient_mag = spectral_grad
    reps.extras["pipeline"] = "IIRS-PCA"
    reps.extras["pca_composite"] = composite
    notes.append("Dimensionality reduction: PCA on valid spectral bands.")
    return IIRSResult(
        representations=reps,
        explained_variance=ev,
        retained_variance=float(sum(ev)),
        n_components=k,
        valid_bands=int(mask.sum()),
        total_bands=b,
        pc_maps=pcs,
        pca_composite=composite,
        notes=notes,
    )
