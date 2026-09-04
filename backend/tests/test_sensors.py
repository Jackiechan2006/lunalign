from pathlib import Path

import numpy as np
from PIL import Image

from core.sensors.iirs import load_iirs
from core.sensors.ohrc import load_ohrc
from core.sensors.tmc import load_tmc
from core.sensors.quality import assess_product


def _save_gray(path: Path, arr: np.ndarray):
    Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(path)


def test_ohrc_loader(tmp_path):
    p = tmp_path / "ohrc_sample.png"
    _save_gray(p, np.linspace(0, 1, 64 * 80).reshape(64, 80))
    prod = load_ohrc(str(p))
    assert prod.metadata.sensor == "OHRC"
    assert prod.image.shape == (64, 80)
    q = assess_product(prod)
    assert q.ok


def test_tmc_loader(tmp_path):
    p = tmp_path / "tmc_sample.png"
    _save_gray(p, np.random.default_rng(0).random((48, 48)))
    prod = load_tmc(str(p))
    assert prod.metadata.sensor == "TMC"


def test_iirs_loader(tmp_path):
    cube = np.random.default_rng(1).random((32, 32, 12)).astype(np.float32)
    p = tmp_path / "iirs_cube.npy"
    np.save(p, cube)
    prod = load_iirs(str(p))
    assert prod.metadata.sensor == "IIRS"
    assert prod.cube is not None and prod.cube.shape[2] == 12
