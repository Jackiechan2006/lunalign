from pydantic import BaseModel, Field
from typing import Optional


class ManualMetadata(BaseModel):
    sensor: Optional[str] = None
    acquisition: Optional[str] = None
    gsd_m: Optional[float] = None
    sun_azimuth_deg: Optional[float] = None
    sun_elevation_deg: Optional[float] = None
    view_azimuth_deg: Optional[float] = None
    view_elevation_deg: Optional[float] = None
    crs: Optional[str] = None
    wavelengths_nm: Optional[list[float]] = None


class QualityWeights(BaseModel):
    inlier_ratio: float = 0.22
    rmse: float = 0.18
    median_error: float = 0.10
    coverage: float = 0.16
    ncc: float = 0.14
    descriptor: float = 0.08
    stability: float = 0.06
    subpixel: float = 0.06
