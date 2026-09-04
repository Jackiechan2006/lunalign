from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from core.matching.knn import MatchSet
from core.preprocessing.normalize import to_uint8


@dataclass
class DeepStatus:
    available: bool
    name: str
    checkpoint: Optional[str]
    message: str
    family: str = "Deep Learning"


def _checkpoint_exists(path: str | None) -> bool:
    if not path:
        return False
    return Path(path).is_file()


def loftr_status(checkpoint: str | None) -> DeepStatus:
    if not _checkpoint_exists(checkpoint):
        return DeepStatus(
            False,
            "LoFTR",
            checkpoint,
            "LoFTR checkpoint unavailable. Falling back to SIFT/RootSIFT. "
            "No automatic weight download (offline policy).",
        )
    try:
        import torch  # noqa: F401
        import kornia  # noqa: F401
    except ImportError:
        return DeepStatus(
            False,
            "LoFTR",
            checkpoint,
            "PyTorch/Kornia not installed. Deep matcher unavailable. Classical fallback.",
        )
    return DeepStatus(True, "LoFTR", checkpoint, "LoFTR local checkpoint detected.")


def superpoint_status(sp_ckpt: str | None, sg_ckpt: str | None) -> DeepStatus:
    if not _checkpoint_exists(sp_ckpt) or not _checkpoint_exists(sg_ckpt):
        return DeepStatus(
            False,
            "SuperPoint+SuperGlue",
            sp_ckpt,
            "SuperPoint/SuperGlue checkpoints unavailable. Falling back to SIFT/RootSIFT.",
        )
    try:
        import torch  # noqa: F401
    except ImportError:
        return DeepStatus(
            False,
            "SuperPoint+SuperGlue",
            sp_ckpt,
            "PyTorch not installed. Deep matcher unavailable. Classical fallback.",
        )
    return DeepStatus(True, "SuperPoint+SuperGlue", sp_ckpt, "Local SuperPoint/SuperGlue checkpoints detected.")


def run_loftr(img1: np.ndarray, img2: np.ndarray, checkpoint: str) -> MatchSet:
    """Optional LoFTR via Kornia. Requires a user-supplied local checkpoint."""
    import torch
    from kornia.feature import LoFTR

    device = "cuda" if torch.cuda.is_available() else "cpu"
    matcher = LoFTR(pretrained=None)
    state = torch.load(checkpoint, map_location=device)
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    matcher.load_state_dict(state, strict=False)
    matcher.eval().to(device)
    a = torch.from_numpy(to_uint8(img1)).float()[None, None] / 255.0
    b = torch.from_numpy(to_uint8(img2)).float()[None, None] / 255.0
    # LoFTR typically expects ~480-640
    def _resize(t, max_side=640):
        h, w = t.shape[-2:]
        scale = max_side / max(h, w)
        nh, nw = int(h * scale), int(w * scale)
        nh, nw = nh - nh % 8, nw - nw % 8
        return torch.nn.functional.interpolate(t, size=(nh, nw), mode="bilinear", align_corners=False), scale

    a2, sa = _resize(a.to(device))
    b2, sb = _resize(b.to(device))
    with torch.no_grad():
        out = matcher({"image0": a2, "image1": b2})
    mk0 = out["keypoints0"].detach().cpu().numpy() / sa
    mk1 = out["keypoints1"].detach().cpu().numpy() / sb
    conf = out.get("confidence")
    conf = conf.detach().cpu().numpy() if conf is not None else np.ones(len(mk0))
    keep = conf > 0.3
    mk0, mk1, conf = mk0[keep], mk1[keep], conf[keep]
    n = len(mk0)
    return MatchSet(
        src_idx=np.arange(n),
        dst_idx=np.arange(n),
        src_pts=mk0.astype(np.float32),
        dst_pts=mk1.astype(np.float32),
        distances=1.0 - conf.astype(np.float32),
        ratios=np.full(n, 0.5, dtype=np.float32),
        raw_count=n,
        ratio_count=n,
        mutual_count=n,
        matcher="LoFTR",
    )


def run_deep_or_skip(img1, img2, checkpoint, kind="loftr") -> tuple[Optional[MatchSet], DeepStatus]:
    if kind == "loftr":
        st = loftr_status(checkpoint)
        if not st.available:
            return None, st
        try:
            return run_loftr(img1, img2, checkpoint), st
        except Exception as exc:  # noqa: BLE001
            return None, DeepStatus(False, "LoFTR", checkpoint, f"LoFTR failed: {exc}. Classical fallback.")
    st = superpoint_status(checkpoint, checkpoint)
    return None, st
