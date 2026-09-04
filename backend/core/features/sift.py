from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np

from core.preprocessing.normalize import to_uint8


@dataclass
class FeatureSet:
    keypoints: list
    descriptors: Optional[np.ndarray]
    points: np.ndarray
    scales: np.ndarray
    orientations: np.ndarray
    detector: str
    descriptor_name: str

    def to_summary(self) -> dict:
        return {
            "n_keypoints": int(len(self.keypoints)),
            "detector": self.detector,
            "descriptor": self.descriptor_name,
        }


def _sift():
    if hasattr(cv2, "SIFT_create"):
        return cv2.SIFT_create(nfeatures=8000)
    raise RuntimeError("OpenCV SIFT unavailable. Install opencv-contrib-python.")


def extract_sift(image: np.ndarray, nfeatures: int = 8000) -> FeatureSet:
    sift = cv2.SIFT_create(nfeatures=nfeatures)
    u8 = to_uint8(image)
    kps, desc = sift.detectAndCompute(u8, None)
    if not kps:
        return FeatureSet([], None, np.zeros((0, 2)), np.zeros(0), np.zeros(0), "SIFT", "SIFT")
    pts = np.array([kp.pt for kp in kps], dtype=np.float32)
    scales = np.array([kp.size for kp in kps], dtype=np.float32)
    ori = np.array([kp.angle for kp in kps], dtype=np.float32)
    return FeatureSet(kps, desc, pts, scales, ori, "SIFT", "SIFT")


def rootsift(descriptors: np.ndarray, eps: float = 1e-7) -> np.ndarray:
    """RootSIFT: L1 normalize each descriptor, then Hellinger (sqrt) mapping.

    Relja Arandjelović & Andrew Zisserman, BMVC 2012.
    This is a classical descriptor normalization, not a neural network.
    """
    if descriptors is None or descriptors.size == 0:
        return descriptors
    d = descriptors.astype(np.float32)
    d = d / (np.sum(np.abs(d), axis=1, keepdims=True) + eps)
    return np.sqrt(d)


def extract_rootsift(image: np.ndarray, nfeatures: int = 8000) -> FeatureSet:
    fs = extract_sift(image, nfeatures=nfeatures)
    if fs.descriptors is not None:
        fs.descriptors = rootsift(fs.descriptors)
        fs.descriptor_name = "RootSIFT"
    return fs


def extract_multiscale_rootsift(pyramid: list[np.ndarray], nfeatures: int = 4000) -> FeatureSet:
    """SIFT on a Gaussian pyramid; coordinates mapped back to level-0."""
    all_kps = []
    all_desc = []
    all_pts = []
    all_sc = []
    all_ori = []
    for level, img in enumerate(pyramid):
        fs = extract_rootsift(img, nfeatures=nfeatures)
        if fs.descriptors is None or len(fs.keypoints) == 0:
            continue
        scale = 2.0 ** level
        pts = fs.points * scale
        for kp in fs.keypoints:
            kp.pt = (kp.pt[0] * scale, kp.pt[1] * scale)
            kp.size *= scale
        all_kps.extend(fs.keypoints)
        all_desc.append(fs.descriptors)
        all_pts.append(pts)
        all_sc.append(fs.scales * scale)
        all_ori.append(fs.orientations)
    if not all_desc:
        return FeatureSet([], None, np.zeros((0, 2)), np.zeros(0), np.zeros(0), "SIFT", "RootSIFT")
    return FeatureSet(
        all_kps,
        np.vstack(all_desc),
        np.vstack(all_pts),
        np.concatenate(all_sc),
        np.concatenate(all_ori),
        "SIFT-multiscale",
        "RootSIFT",
    )
