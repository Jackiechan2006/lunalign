from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image


@dataclass
class DEMProduct:
    z: np.ndarray
    kind: str  # REAL_DEM | DERIVED_DEM | SYNTHETIC_DEM
    path: Optional[str]
    transform: Optional[list]
    crs: Optional[str]
    notes: list[str]

    def to_dict(self) -> dict:
        h, w = self.z.shape[:2]
        finite = self.z[np.isfinite(self.z)]
        return {
            "kind": self.kind,
            "path": self.path,
            "width": int(w),
            "height": int(h),
            "z_min": float(finite.min()) if finite.size else None,
            "z_max": float(finite.max()) if finite.size else None,
            "crs": self.crs,
            "notes": self.notes,
            "label": _label(self.kind),
        }


def _label(kind: str) -> str:
    if kind == "REAL_DEM":
        return "REAL DEM"
    if kind == "DERIVED_DEM":
        return "DERIVED DEM"
    if kind == "SYNTHETIC_DEM":
        return "SYNTHETIC DEM — NOT SCIENTIFIC DATA"
    return "DEM unavailable"


def load_dem(path: str | Path, kind: str = "REAL_DEM") -> DEMProduct:
    path = Path(path)
    suffix = path.suffix.lower()
    notes = []
    crs = None
    transform = None
    if suffix in {".npy"}:
        z = np.load(path).astype(np.float32)
    elif suffix in {".tif", ".tiff"}:
        try:
            import tifffile

            z = np.asarray(tifffile.imread(str(path))).astype(np.float32)
            notes.append("Loaded GeoTIFF/TIFF DEM via tifffile.")
        except Exception:
            z = np.array(Image.open(path)).astype(np.float32)
        if z.ndim == 3:
            z = z[..., 0]
        try:
            import rasterio

            with rasterio.open(path) as ds:
                crs = str(ds.crs) if ds.crs else None
                transform = list(ds.transform)
        except Exception:
            notes.append("GDAL/rasterio unavailable; georeferencing may be incomplete.")
    else:
        z = np.array(Image.open(path)).astype(np.float32)
        if z.ndim == 3:
            z = z[..., 0]
    if kind == "SYNTHETIC_DEM":
        notes.append("SYNTHETIC DEM — NOT SCIENTIFIC DATA. Do not use in SIH performance claims.")
    elif kind == "REAL_DEM":
        notes.append("User-supplied DEM treated as REAL DEM. Accuracy depends on the source product.")
    return DEMProduct(z=z, kind=kind, path=str(path), transform=transform, crs=crs, notes=notes)


def synthetic_dem(shape: tuple[int, int], seed: int = 42) -> DEMProduct:
    rng = np.random.default_rng(seed)
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    z = (
        120 * np.exp(-((xx - w * 0.4) ** 2 + (yy - h * 0.45) ** 2) / (2 * (0.18 * w) ** 2))
        + 80 * np.exp(-((xx - w * 0.7) ** 2 + (yy - h * 0.6) ** 2) / (2 * (0.12 * w) ** 2))
        + rng.normal(0, 1.5, size=(h, w))
    ).astype(np.float32)
    return DEMProduct(
        z=z,
        kind="SYNTHETIC_DEM",
        path=None,
        transform=None,
        crs=None,
        notes=["SYNTHETIC DEM — NOT SCIENTIFIC DATA. Development/testing only."],
    )


def derive_dem_from_image(image: np.ndarray) -> DEMProduct:
    import cv2
    img = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = img.astype(np.float32)
    if gray.max() > 1.0:
        gray = gray / 255.0
    blur_large = cv2.GaussianBlur(gray, (0, 0), sigmaX=8.0)
    blur_small = cv2.GaussianBlur(gray, (0, 0), sigmaX=2.0)
    # Shape-from-shading elevation proxy
    z = (1.0 - blur_large) * 50.0 + (gray - blur_small) * 30.0
    z = cv2.GaussianBlur(z.astype(np.float32), (0, 0), sigmaX=3.0)
    notes = ["DERIVED DEM — Estimated automatically from reference image illumination & shading gradients."]
    return DEMProduct(z=z, kind="DERIVED_DEM", path=None, transform=None, crs=None, notes=notes)



def sample_z(dem: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    xi = np.clip(np.round(x).astype(int), 0, dem.shape[1] - 1)
    yi = np.clip(np.round(y).astype(int), 0, dem.shape[0] - 1)
    return dem[yi, xi]


def dem_consistency(
    dem: np.ndarray,
    src: np.ndarray,
    dst: np.ndarray,
    max_dz: float = 80.0,
) -> dict:
    """Compare elevations at corresponding 2D points. Optional constraint only."""
    z1 = sample_z(dem, src[:, 0], src[:, 1])
    # dst may live in a different raster; if same DEM assumed, sample dst as well
    z2 = sample_z(dem, dst[:, 0] * (dem.shape[1] / max(dst[:, 0].max() + 1, 1)), dst[:, 1] * (dem.shape[0] / max(dst[:, 1].max() + 1, 1))) if False else sample_z(dem, np.clip(dst[:, 0], 0, dem.shape[1] - 1), np.clip(dst[:, 1], 0, dem.shape[0] - 1))
    dz = np.abs(z1 - z2)
    mean_res = float(np.nanmean(dz)) if dz.size else None
    boost = np.clip(1.0 - dz / max_dz, 0, 1)
    return {
        "mean_residual": mean_res,
        "median_residual": float(np.nanmedian(dz)) if dz.size else None,
        "per_point": dz.tolist(),
        "confidence_mod": boost.tolist(),
        "note": "DEM-assisted geometric consistency is optional and assumes correspondences can be associated with the same DEM grid.",
    }


def mesh_preview(dem: np.ndarray, stride: int = 8) -> dict:
    z = dem[::stride, ::stride]
    h, w = z.shape
    yy, xx = np.mgrid[0:h, 0:w]
    positions = np.stack([xx.ravel(), yy.ravel(), z.ravel()], axis=1)
    return {
        "width": int(w),
        "height": int(h),
        "stride": stride,
        "positions": positions.astype(np.float32).tolist(),
        "z_min": float(np.nanmin(z)),
        "z_max": float(np.nanmax(z)),
    }
