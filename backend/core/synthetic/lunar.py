"""Synthetic lunar-like scenes for pipeline validation. Never labeled as mission data."""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class SyntheticPair:
    reference: np.ndarray
    moving: np.ndarray
    matrix: np.ndarray
    model: str
    ref_meta: dict
    mov_meta: dict
    notes: list[str]


def crater_field(h: int = 384, w: int = 384, seed: int = 42, light_az: float = 120.0, light_el: float = 40.0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w]
    height = rng.normal(0, 0.02, size=(h, w)).astype(np.float32)
    n_craters = 28
    for _ in range(n_craters):
        cx, cy = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(8, 48)
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        bowl = np.clip(1 - (d / r) ** 2, 0, 1)
        depth = rng.uniform(0.15, 0.7)
        height -= depth * bowl
        rim = np.exp(-((d - r) ** 2) / (2 * (0.12 * r) ** 2)) * rng.uniform(0.05, 0.18)
        height += rim
    height = cv2.GaussianBlur(height, (0, 0), 1.2)
    az = np.deg2rad(light_az)
    el = np.deg2rad(light_el)
    lx, ly, lz = np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)
    gy, gx = np.gradient(height)
    nx, ny, nz = -gx, -gy, np.ones_like(height)
    nrm = np.sqrt(nx * nx + ny * ny + nz * nz)
    shade = np.clip((nx * lx + ny * ly + nz * lz) / nrm, 0, 1)
    albedo = 0.35 + 0.08 * rng.normal(0, 1, size=(h, w))
    albedo = cv2.GaussianBlur(albedo.astype(np.float32), (0, 0), 2.0)
    img = np.clip(albedo * (0.25 + 0.75 * shade), 0, 1)
    return img.astype(np.float32)


def make_pair(
    seed: int = 42,
    scale: float = 1.15,
    rotation_deg: float = 8.0,
    tx: float = 12.0,
    ty: float = -9.0,
    light_ref: tuple[float, float] = (110.0, 42.0),
    light_mov: tuple[float, float] = (155.0, 28.0),
    size: int = 384,
) -> SyntheticPair:
    ref = crater_field(size, size, seed=seed, light_az=light_ref[0], light_el=light_ref[1])
    base = crater_field(size, size, seed=seed, light_az=light_mov[0], light_el=light_mov[1])
    M = cv2.getRotationMatrix2D((size / 2, size / 2), rotation_deg, scale)
    M[0, 2] += tx
    M[1, 2] += ty
    moving = cv2.warpAffine(base, M, (size, size), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    notes = [
        "SYNTHETIC BENCHMARK — generated crater-shaded imagery, not Chandrayaan-2 measurements.",
        "Ground truth is a known similarity transform used only to validate software.",
    ]
    return SyntheticPair(
        reference=ref,
        moving=moving,
        matrix=M,
        model="similarity",
        ref_meta={
            "sensor": "OHRC",
            "gsd_m": 0.32,
            "sun_azimuth_deg": light_ref[0],
            "sun_elevation_deg": light_ref[1],
            "acquisition": "2019-09-06",
        },
        mov_meta={
            "sensor": "TMC",
            "gsd_m": 5.0 * (1.0 / scale),
            "sun_azimuth_deg": light_mov[0],
            "sun_elevation_deg": light_mov[1],
            "acquisition": "2019-09-06",
        },
        notes=notes,
    )
