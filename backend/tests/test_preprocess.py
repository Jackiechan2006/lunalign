import numpy as np

from core.preprocessing.iirs import preprocess_iirs
from core.preprocessing.normalize import clahe, percentile_stretch
from core.preprocessing.optical import preprocess_ohrc


def test_normalization_range():
    x = np.linspace(10, 90, 100).reshape(10, 10).astype(np.float32)
    y = percentile_stretch(x)
    assert y.min() >= 0 and y.max() <= 1
    c = clahe(x)
    assert c.shape == x.shape


def test_ohrc_representations():
    img = np.random.default_rng(2).random((64, 64)).astype(np.float32)
    r = preprocess_ohrc(img)
    assert r.clahe.shape == img.shape
    assert len(r.pyramid) >= 3


def test_iirs_pca_variance():
    rng = np.random.default_rng(3)
    h, w, b = 24, 24, 16
    base = rng.random((h, w, 3))
    cube = np.concatenate([base, rng.normal(0, 0.05, (h, w, b - 3))], axis=2).astype(np.float32)
    out = preprocess_iirs(cube, n_components=3)
    assert out.n_components == 3
    assert len(out.explained_variance) == 3
    assert 0 < out.retained_variance <= 1.0001
    assert out.pca_composite is not None
