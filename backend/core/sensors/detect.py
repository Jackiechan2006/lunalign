from __future__ import annotations

from core.sensors.loaders import load_product
from core.sensors.ohrc import load_ohrc
from core.sensors.tmc import load_tmc
from core.sensors.iirs import load_iirs


def load_by_sensor(path: str, sensor: str | None, **kwargs):
    s = (sensor or "").upper()
    if s == "OHRC":
        return load_ohrc(path, **kwargs)
    if s in {"TMC", "TMC-2", "TMC2"}:
        return load_tmc(path, **kwargs)
    if s == "IIRS":
        return load_iirs(path, **kwargs)
    return load_product(path, sensor_hint=sensor, **kwargs)
