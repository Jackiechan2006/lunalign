from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import numpy as np

from core.sensors.base import Metadata, SensorName


def load_sidecar_metadata(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    for cand in (p.with_suffix(".json"), Path(str(p) + ".json"), p.with_suffix(".lbl")):
        if cand.exists() and cand.suffix.lower() == ".json":
            return json.loads(cand.read_text(encoding="utf-8"))
    return {}


def metadata_from_mapping(raw: dict[str, Any], fallback: Metadata | None = None) -> Metadata:
    m = fallback or Metadata()
    sensor = str(raw.get("sensor") or raw.get("SENSOR") or m.sensor).upper()
    if sensor in {"OHRC", "TMC", "TMC-2", "TMC2"}:
        m.sensor = "TMC" if sensor.startswith("TMC") else "OHRC"
    elif sensor == "IIRS":
        m.sensor = "IIRS"
    m.acquisition = raw.get("acquisition") or raw.get("acquisition_time") or m.acquisition
    m.gsd_m = _f(raw.get("gsd_m") or raw.get("gsd") or raw.get("spatial_resolution_m"), m.gsd_m)
    m.sun_azimuth_deg = _f(raw.get("sun_azimuth_deg") or raw.get("sun_azimuth"), m.sun_azimuth_deg)
    m.sun_elevation_deg = _f(
        raw.get("sun_elevation_deg") or raw.get("sun_elevation"), m.sun_elevation_deg
    )
    m.view_azimuth_deg = _f(raw.get("view_azimuth_deg"), m.view_azimuth_deg)
    m.view_elevation_deg = _f(raw.get("view_elevation_deg"), m.view_elevation_deg)
    m.crs = raw.get("crs") or m.crs
    wl = raw.get("wavelengths_nm") or raw.get("wavelengths")
    if isinstance(wl, list):
        m.wavelengths_nm = [float(x) for x in wl]
    return m


def _f(v: Any, default: Optional[float]) -> Optional[float]:
    if v is None or v == "":
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def infer_sensor(filename: str, image: np.ndarray, meta: Metadata) -> SensorName:
    if meta.sensor != "UNKNOWN":
        return meta.sensor
    name = filename.lower()
    if "ohrc" in name:
        return "OHRC"
    if "iirs" in name or "hyper" in name:
        return "IIRS"
    if "tmc" in name:
        return "TMC"
    if image.ndim == 3 and image.shape[2] > 4:
        return "IIRS"
    if image.ndim == 2:
        h, w = image.shape[:2]
        if min(h, w) >= 2048:
            return "OHRC"
        return "TMC"
    return "UNKNOWN"
