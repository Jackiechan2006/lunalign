from __future__ import annotations

from typing import Optional


def azimuth_difference_deg(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None:
        return None
    d = abs(float(a) - float(b)) % 360.0
    return min(d, 360.0 - d)


def elevation_difference_deg(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None:
        return None
    return abs(float(a) - float(b))


def illumination_severity(
    d_az: Optional[float],
    d_el: Optional[float],
    large_az: float = 40.0,
    large_el: float = 20.0,
) -> str:
    if d_az is None and d_el is None:
        return "unknown"
    az = d_az or 0.0
    el = d_el or 0.0
    if az >= large_az or el >= large_el:
        return "large"
    if az >= large_az * 0.5 or el >= large_el * 0.5:
        return "moderate"
    return "small"


def representation_guidance(severity: str) -> dict:
    """Guide representation weights from sun-angle metadata. Not an invariance claim."""
    if severity == "large":
        return {
            "prefer": ["gradient_mag", "gradient_ori", "phase_proxy", "edges", "lcn"],
            "reason": "Large sun-angle difference: emphasize gradient/phase over raw intensity.",
        }
    if severity == "moderate":
        return {
            "prefer": ["clahe", "lcn", "gradient_mag"],
            "reason": "Moderate illumination difference: CLAHE + LCN + gradients.",
        }
    if severity == "unknown":
        return {
            "prefer": ["clahe", "lcn", "gradient_mag"],
            "reason": "Sun metadata missing: default illumination-robust representations.",
        }
    return {
        "prefer": ["clahe", "intensity"],
        "reason": "Small sun-angle difference: CLAHE-normalized intensity is sufficient.",
    }
