"""Cross-modal integration on synthetic stand-ins. Real mission data required for scientific validation."""
from pathlib import Path

import cv2
import numpy as np

from app.services.pipeline import run_registration
from core.synthetic.lunar import make_pair


def _write_pair(tmp: Path, scale=0.85):
    pair = make_pair(seed=21, scale=scale, rotation_deg=5.0, size=256)
    ref = tmp / "ref.png"
    mov = tmp / "mov.png"
    cv2.imwrite(str(ref), (pair.reference * 255).astype(np.uint8))
    cv2.imwrite(str(mov), (pair.moving * 255).astype(np.uint8))
    cube = np.stack([pair.moving, cv2.GaussianBlur(pair.moving, (0, 0), 1.5), pair.moving * 0.8], axis=-1)
    # expand to 8 bands
    extra = [pair.moving * (0.7 + 0.05 * i) for i in range(5)]
    cube = np.stack([pair.moving, *extra, pair.moving], axis=-1).astype(np.float32)
    npy = tmp / "iirs.npy"
    np.save(npy, cube)
    return ref, mov, npy, pair


def test_ohrc_tmc_pipeline(tmp_path):
    ref, mov, _, pair = _write_pair(tmp_path)
    res = run_registration(
        str(ref),
        str(mov),
        ref_sensor="OHRC",
        mov_sensor="TMC",
        ref_meta=pair.ref_meta,
        mov_meta=pair.mov_meta,
        origin="SYNTHETIC_BENCHMARK",
        mode="classical",
        out_dir=tmp_path / "out",
    )
    assert res["ok"]
    assert res["origin_label"] == "SYNTHETIC BENCHMARK"
    assert res["geometry"]["inliers"] >= 8
    assert res["quality"]["score"] is not None
    assert "Classical" in res["algorithm"]["family"] or res["algorithm"]["deep_model"] == "Not used"


def test_ohrc_iirs_pipeline(tmp_path):
    ref, _, iirs, pair = _write_pair(tmp_path)
    res = run_registration(
        str(ref),
        str(iirs),
        ref_sensor="OHRC",
        mov_sensor="IIRS",
        ref_meta=pair.ref_meta,
        mov_meta={**pair.mov_meta, "sensor": "IIRS"},
        origin="SYNTHETIC_BENCHMARK",
        mode="classical",
        out_dir=tmp_path / "out2",
    )
    assert res["ok"]
    assert res["moving"]["iirs"] is not None or res["moving"]["metadata"]["sensor"] == "IIRS"


def test_tmc_iirs_pipeline(tmp_path):
    ref, mov, iirs, pair = _write_pair(tmp_path)
    res = run_registration(
        str(mov),
        str(iirs),
        ref_sensor="TMC",
        mov_sensor="IIRS",
        origin="SYNTHETIC_BENCHMARK",
        mode="classical",
        out_dir=tmp_path / "out3",
    )
    assert res["ok"]
    assert res["origin"] == "SYNTHETIC_BENCHMARK"
