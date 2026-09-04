from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional

import numpy as np

SensorName = Literal["OHRC", "TMC", "IIRS", "UNKNOWN"]
DataOrigin = Literal["REAL_CHANDRAYAAN2", "SYNTHETIC_BENCHMARK"]
DemKind = Literal["REAL_DEM", "DERIVED_DEM", "SYNTHETIC_DEM", "NONE"]


@dataclass
class Metadata:
    sensor: SensorName = "UNKNOWN"
    acquisition: Optional[str] = None
    gsd_m: Optional[float] = None
    sun_azimuth_deg: Optional[float] = None
    sun_elevation_deg: Optional[float] = None
    view_azimuth_deg: Optional[float] = None
    view_elevation_deg: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    crs: Optional[str] = None
    wavelengths_nm: Optional[list[float]] = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sensor": self.sensor,
            "acquisition": self.acquisition,
            "gsd_m": self.gsd_m,
            "sun_azimuth_deg": self.sun_azimuth_deg,
            "sun_elevation_deg": self.sun_elevation_deg,
            "view_azimuth_deg": self.view_azimuth_deg,
            "view_elevation_deg": self.view_elevation_deg,
            "width": self.width,
            "height": self.height,
            "crs": self.crs,
            "wavelengths_nm": self.wavelengths_nm,
            "extra": self.extra,
        }


@dataclass
class LoadedProduct:
    image: np.ndarray  # 2D float32 working image or HxWxB cube for IIRS
    preview: np.ndarray  # 2D uint8/float visualization
    metadata: Metadata
    path: str
    origin: DataOrigin = "REAL_CHANDRAYAAN2"
    cube: Optional[np.ndarray] = None
    notes: list[str] = field(default_factory=list)
