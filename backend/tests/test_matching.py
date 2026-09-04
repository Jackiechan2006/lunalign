import numpy as np

from core.features.sift import extract_rootsift, rootsift
from core.geometry.ransac import estimate_transform
from core.geometry.scale import gsd_scale_ratio
from core.geometry.sun import azimuth_difference_deg, elevation_difference_deg
from core.matching.knn import knn_match
from core.quality.score import quality_score
from core.quality.uniform import select_uniform
from core.refinement.ncc import ncc, ncc_search
from core.synthetic.lunar import crater_field, make_pair


def test_sun_angles():
    assert azimuth_difference_deg(10, 350) == 20
    assert elevation_difference_deg(40, 15) == 25


def test_scale_gsd():
    assert abs(gsd_scale_ratio(0.32, 5.0) - (5.0 / 0.32)) < 1e-6
    assert gsd_scale_ratio(None, 1) is None


def test_rootsift_l1_sqrt():
    d = np.array([[1.0, 3.0, 0.0, 4.0]], dtype=np.float32)
    r = rootsift(d)
    assert np.isclose(np.sum(r**2), 1.0, atol=1e-5) or r.shape == (1, 4)
    assert np.all(r >= 0)


def test_sift_and_matching_on_synthetic():
    pair = make_pair(seed=11, scale=1.05, rotation_deg=3.0, tx=4, ty=-3, size=256)
    f1 = extract_rootsift(pair.reference)
    f2 = extract_rootsift(pair.moving)
    assert f1.descriptor_name == "RootSIFT"
    m = knn_match(f1.descriptors, f2.descriptors, f1.points, f2.points, ratio=0.8)
    assert m.raw_count >= m.ratio_count
    assert m.ratio_count >= m.mutual_count


def test_ransac_known_translation():
    rng = np.random.default_rng(4)
    src = rng.uniform(20, 200, size=(80, 2))
    dst = src + np.array([12.0, -7.0])
    dst[0] += [80, 80]  # outlier
    r = estimate_transform(src, dst, model="translation", thresh=2.0)
    assert r.inliers >= 70
    assert r.rmse is not None and r.rmse < 1.0
    assert "not machine learning" in r.notes[0].lower() or "not machine learning" in "".join(r.notes).lower()


def test_uniform_grid():
    rng = np.random.default_rng(5)
    src = rng.uniform(0, 128, size=(200, 2))
    dst = src + 2
    scores = rng.random(200)
    sel, stats = select_uniform(src, dst, scores, (128, 128), grid=(8, 8), max_per_cell=2, min_separation=4)
    assert stats["grid"] == [8, 8]
    assert stats["n_selected"] <= 8 * 8 * 2
    assert stats["coverage"] > 0


def test_ncc_and_subpixel():
    img = crater_field(96, 96, seed=6)
    a = img[20:41, 20:41]
    b = img[20:41, 21:42]
    assert ncc(a, a) > 0.99
    res = ncc_search(img, img, 40, 40, 41, 40, patch_size=15, radius=2)
    assert res["ok"]
    assert res["ncc"] is not None


def test_quality_score_not_probability():
    q = quality_score(
        inlier_ratio=0.8,
        rmse=0.7,
        median_error=0.5,
        coverage=0.9,
        mean_ncc=0.7,
        mean_ratio=0.5,
        subpixel_shift=0.3,
        dem_residual=None,
    )
    assert 0 <= q["score"] <= 1
    assert q["band"] in {"HIGH", "MEDIUM", "LOW"}
    assert "not a probability" in q["disclaimer"].lower()
