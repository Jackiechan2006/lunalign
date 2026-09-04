from __future__ import annotations

from core.sensors.loaders import load_product


def load_ohrc(path: str, **kwargs):
    return load_product(path, sensor_hint="OHRC", **kwargs)
