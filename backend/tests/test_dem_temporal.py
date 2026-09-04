import numpy as np

from core.dem.loader import dem_consistency, load_dem, synthetic_dem
from core.temporal.index import potential_change, timeline_marks


def test_synthetic_dem_label():
    d = synthetic_dem((32, 32), seed=1)
    assert d.kind == "SYNTHETIC_DEM"
    assert "NOT SCIENTIFIC" in d.to_dict()["label"]


def test_dem_load_npy(tmp_path):
    z = np.arange(64, dtype=np.float32).reshape(8, 8)
    p = tmp_path / "dem.npy"
    np.save(p, z)
    d = load_dem(p, kind="REAL_DEM")
    assert d.z.shape == (8, 8)
    assert d.kind == "REAL_DEM"


def test_dem_consistency():
    dem = synthetic_dem((40, 40)).z
    src = np.array([[10.0, 10.0], [20.0, 12.0]])
    dst = np.array([[10.0, 10.0], [21.0, 12.0]])
    c = dem_consistency(dem, src, dst)
    assert c["mean_residual"] is not None


def test_temporal_potential_not_confirmed():
    z1 = np.zeros((16, 16))
    z2 = np.ones((16, 16)) * 3
    out = potential_change(z1, z2, "large", rmse_px=2.0)
    assert out["kind"] == "Potential Surface Change"
    assert "Confirmed" in out["not"]
    assert timeline_marks()[0] == 2010
