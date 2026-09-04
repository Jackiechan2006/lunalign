from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from core.sensors.base import LoadedProduct


@dataclass
class QualityCheck:
    ok: bool
    items: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "items": self.items,
            "warnings": self.warnings,
            "errors": self.errors,
        }


def assess_product(product: LoadedProduct) -> QualityCheck:
    items: list[dict[str, Any]] = []
    warnings: list[str] = []
    errors: list[str] = []
    img = product.image
    readable = img is not None and img.size > 0
    items.append({"key": "readable", "ok": readable, "label": "Image readable"})
    if not readable:
        errors.append("Image could not be read.")
        return QualityCheck(False, items, warnings, errors)

    h, w = img.shape[:2]
    dim_ok = h >= 32 and w >= 32
    items.append(
        {
            "key": "dimensions",
            "ok": dim_ok,
            "label": "Dimensions valid",
            "detail": f"{w} × {h}",
        }
    )
    if not dim_ok:
        errors.append("Image is too small for reliable correspondence (minimum 32×32).")

    nan_frac = float(np.isnan(img).mean()) if np.issubdtype(img.dtype, np.floating) else 0.0
    nan_ok = nan_frac < 0.25
    items.append(
        {
            "key": "nans",
            "ok": nan_ok,
            "label": "No critical NaNs",
            "detail": f"{nan_frac:.2%} invalid",
        }
    )
    if not nan_ok:
        errors.append("Too many NaN/invalid pixels for matching.")
    elif nan_frac > 0:
        warnings.append(f"Invalid pixels present ({nan_frac:.2%}).")

    finite = img[np.isfinite(img)]
    if finite.size:
        dr = float(finite.max() - finite.min())
        items.append(
            {
                "key": "dynamic_range",
                "ok": dr > 0,
                "label": "Dynamic range detected",
                "detail": f"min={finite.min():.4g} max={finite.max():.4g}",
            }
        )
        if dr == 0:
            errors.append("Zero dynamic range (constant image).")
    else:
        errors.append("No finite pixels.")

    meta = product.metadata
    meta_fields = [
        meta.sensor != "UNKNOWN",
        meta.gsd_m is not None,
        meta.sun_azimuth_deg is not None,
        meta.sun_elevation_deg is not None,
        meta.acquisition is not None,
    ]
    items.append(
        {
            "key": "metadata",
            "ok": any(meta_fields),
            "label": "Metadata available",
            "detail": "present" if any(meta_fields) else "none extracted",
        }
    )
    if meta.sun_azimuth_deg is None or meta.sun_elevation_deg is None:
        warnings.append("Sun angle missing — illumination-aware selection will use image statistics only.")
        items.append({"key": "sun", "ok": False, "label": "Sun angle missing", "warn": True})
    else:
        items.append({"key": "sun", "ok": True, "label": "Sun angle present"})

    if product.cube is not None:
        b = product.cube.shape[2]
        invalid_bands = int(np.sum(~np.isfinite(product.cube).any(axis=(0, 1))))
        items.append(
            {
                "key": "bands",
                "ok": invalid_bands < b,
                "label": "Band validation",
                "detail": f"{b - invalid_bands}/{b} usable bands",
            }
        )
        if invalid_bands == b:
            errors.append("IIRS data detected but spectral bands are invalid. Check band metadata or upload a valid IIRS product.")

    ok = len(errors) == 0
    return QualityCheck(ok=ok, items=items, warnings=warnings, errors=errors)
