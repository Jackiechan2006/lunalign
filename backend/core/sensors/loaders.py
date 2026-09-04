from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from core.sensors.base import LoadedProduct, Metadata
from core.sensors.metadata import infer_sensor, load_sidecar_metadata, metadata_from_mapping


def _to_float(arr: np.ndarray) -> np.ndarray:
    a = arr.astype(np.float32)
    if a.ndim == 3 and a.shape[2] in (3, 4):
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        a = 0.2989 * r + 0.5870 * g + 0.1140 * b
    elif a.ndim == 3 and a.shape[2] == 1:
        a = a[..., 0]
    return a


def load_raster(path: str | Path) -> tuple[np.ndarray, dict]:
    path = Path(path)
    extra: dict = {}
    suffix = path.suffix.lower()
    if suffix in {".npy"}:
        arr = np.load(path)
        return arr, extra
    if suffix in {".tif", ".tiff"}:
        try:
            import tifffile

            arr = tifffile.imread(str(path))
            extra["loader"] = "tifffile"
            return np.asarray(arr), extra
        except Exception as exc:  # noqa: BLE001
            extra["tifffile_error"] = str(exc)
        try:
            import rasterio

            with rasterio.open(path) as ds:
                arr = ds.read()
                extra["crs"] = str(ds.crs) if ds.crs else None
                extra["transform"] = list(ds.transform) if ds.transform else None
                extra["loader"] = "rasterio"
            if arr.ndim == 3:
                arr = np.moveaxis(arr, 0, -1)
            return arr, extra
        except Exception as exc:  # noqa: BLE001
            extra["rasterio_error"] = str(exc)
    img = Image.open(path)
    arr = np.array(img)
    extra["loader"] = "pillow"
    extra["mode"] = img.mode
    return arr, extra


def load_product(
    path: str | Path,
    sensor_hint: str | None = None,
    origin: str = "REAL_CHANDRAYAAN2",
    manual_meta: dict | None = None,
) -> LoadedProduct:
    path = Path(path)
    arr, extra = load_raster(path)
    sidecar = load_sidecar_metadata(path)
    meta = metadata_from_mapping({**sidecar, **(manual_meta or {})})
    if extra.get("crs"):
        meta.crs = extra["crs"]
    notes: list[str] = []
    cube = None
    if arr.ndim == 3 and arr.shape[2] > 4:
        cube = arr.astype(np.float32)
        preview = _pca_preview(cube)
        working = preview.astype(np.float32)
        notes.append("Hyperspectral cube loaded; PCA preview generated for visualization.")
        meta.sensor = "IIRS"
    else:
        working = _to_float(arr)
        preview = working
    h, w = working.shape[:2]
    meta.width, meta.height = int(w), int(h)
    if sensor_hint and sensor_hint.upper() in {"OHRC", "TMC", "IIRS"}:
        meta.sensor = sensor_hint.upper()  # type: ignore[assignment]
    else:
        meta.sensor = infer_sensor(path.name, cube if cube is not None else working, meta)
    if origin == "SYNTHETIC_BENCHMARK":
        notes.append("SYNTHETIC BENCHMARK — not Chandrayaan-2 mission measurements.")
    return LoadedProduct(
        image=working.astype(np.float32),
        preview=preview.astype(np.float32),
        metadata=meta,
        path=str(path),
        origin=origin,  # type: ignore[arg-type]
        cube=cube,
        notes=notes,
    )


def _pca_preview(cube: np.ndarray) -> np.ndarray:
    h, w, b = cube.shape
    x = cube.reshape(-1, b)
    finite = np.isfinite(x).all(axis=1)
    if finite.sum() < 16:
        return np.nanmean(cube, axis=2)
    mu = np.nanmean(x[finite], axis=0)
    xc = x - mu
    xc[~finite] = 0
    # First principal component via SVD on a subsample for memory safety.
    idx = np.where(finite)[0]
    if idx.size > 200_000:
        rng = np.random.default_rng(42)
        idx = rng.choice(idx, size=200_000, replace=False)
    u, s, vt = np.linalg.svd(xc[idx], full_matrices=False)
    pc1 = xc @ vt[0]
    img = pc1.reshape(h, w)
    return img
