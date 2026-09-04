from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.services.benchmark import run_synthetic_benchmarks
from app.services.demo import DEMO_STEPS, run_sih_demo
from app.services.jobs import store
from app.services.pipeline import load_config, run_registration
from app.services.reports import write_reports
from core.sensors.detect import load_by_sensor
from core.sensors.quality import assess_product
from core.geometry.sun import azimuth_difference_deg, elevation_difference_deg

router = APIRouter()
ROOT = Path(__file__).resolve().parents[3]


def _save_upload(dest: Path, upload: UploadFile) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = upload.file.read()
    dest.write_bytes(data)
    return dest


def _parse_meta(raw: Optional[str]) -> dict:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


@router.get("/health")
def health():
    return {"ok": True, "name": "LunaAlign-X", "offline_core": True}


@router.get("/config")
def get_config():
    return load_config()


@router.post("/inspect")
async def inspect(
    image: UploadFile = File(...),
    sensor: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
):
    tmp = ROOT / "data" / "processed" / "_inspect" / image.filename
    _save_upload(tmp, image)
    product = load_by_sensor(str(tmp), sensor, manual_meta=_parse_meta(metadata))
    q = assess_product(product)
    return {
        "metadata": product.metadata.to_dict(),
        "quality": q.to_dict(),
        "notes": product.notes,
        "origin_note": "Metadata fields that were not present are left empty; they are not invented.",
    }


@router.post("/jobs")
async def create_job(
    reference: UploadFile = File(...),
    moving: UploadFile = File(...),
    dem: Optional[UploadFile] = File(None),
    ref_sensor: Optional[str] = Form(None),
    mov_sensor: Optional[str] = Form(None),
    ref_meta: Optional[str] = Form(None),
    mov_meta: Optional[str] = Form(None),
    origin: str = Form("REAL_CHANDRAYAAN2"),
    mode: str = Form("automatic"),
    dem_kind: str = Form("REAL_DEM"),
    pca_components: int = Form(3),
):
    job = store.create()
    d = Path(job["dir"])
    ref_path = _save_upload(d / f"ref_{reference.filename}", reference)
    mov_path = _save_upload(d / f"mov_{moving.filename}", moving)
    dem_path = None
    if dem is not None and dem.filename and dem.filename.strip() != "":
        saved_dem = _save_upload(d / f"dem_{dem.filename}", dem)
        if saved_dem.stat().st_size > 0:
            dem_path = str(saved_dem)
        else:
            saved_dem.unlink(missing_ok=True)
            dem_path = None
    job.update(
        {
            "ref_path": str(ref_path),
            "mov_path": str(mov_path),
            "dem_path": dem_path,
            "ref_sensor": ref_sensor,
            "mov_sensor": mov_sensor,
            "ref_meta": _parse_meta(ref_meta),
            "mov_meta": _parse_meta(mov_meta),
            "origin": origin,
            "mode": mode,
            "dem_kind": dem_kind,
            "pca_components": pca_components,
            "status": "queued",
        }
    )
    store.save(job)
    return {"id": job["id"], "status": job["status"]}


@router.post("/jobs/{jid}/run")
def run_job(jid: str):
    job = store.get(jid)
    if not job:
        raise HTTPException(404, "Job not found")
    job["status"] = "running"
    store.save(job)
    try:
        result = run_registration(
            job["ref_path"],
            job["mov_path"],
            ref_sensor=job.get("ref_sensor"),
            mov_sensor=job.get("mov_sensor"),
            ref_meta=job.get("ref_meta"),
            mov_meta=job.get("mov_meta"),
            origin=job.get("origin", "REAL_CHANDRAYAAN2"),
            mode=job.get("mode", "automatic"),
            dem_path=job.get("dem_path"),
            dem_kind=job.get("dem_kind", "REAL_DEM"),
            pca_components=job.get("pca_components"),
            out_dir=Path(job["dir"]) / "previews",
        )
        job["result"] = result
        job["status"] = "done" if result.get("ok") else "failed"
        reports = write_reports(result, Path(job["dir"]) / "reports")
        result["reports"] = reports
        job["result"] = result
    except Exception as exc:  # noqa: BLE001
        job["status"] = "failed"
        job["error"] = str(exc)
        store.save(job)
        raise HTTPException(500, str(exc)) from exc
    store.save(job)
    return job["result"]


@router.get("/jobs/{jid}")
def get_job(jid: str):
    job = store.get(jid)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@router.get("/jobs/{jid}/files/{name}")
def job_file(jid: str, name: str):
    job = store.get(jid)
    if not job:
        raise HTTPException(404, "Job not found")
    for folder in ("previews", "reports"):
        p = Path(job["dir"]) / folder / name
        if p.exists():
            return FileResponse(p)
    raise HTTPException(404, "File not found")


@router.post("/demo/sih")
def sih_demo():
    job = store.create()
    result = run_sih_demo(Path(job["dir"]))
    reports = write_reports(result, Path(job["dir"]) / "reports")
    result["reports"] = reports
    # copy demo previews into expected folder
    run_dir = Path(job["dir"]) / "run"
    preview_dir = Path(job["dir"]) / "previews"
    preview_dir.mkdir(exist_ok=True)
    if run_dir.exists():
        for f in run_dir.glob("*.png"):
            (preview_dir / f.name).write_bytes(f.read_bytes())
    job["result"] = result
    job["status"] = "done"
    job["origin"] = "SYNTHETIC_BENCHMARK"
    store.save(job)
    return {"id": job["id"], "result": result, "steps": DEMO_STEPS}


@router.get("/demo/steps")
def demo_steps():
    return {"steps": DEMO_STEPS}


@router.post("/benchmarks/synthetic")
def synthetic_benchmarks():
    job = store.create()
    table = run_synthetic_benchmarks(Path(job["dir"]) / "bench")
    job["result"] = table
    job["status"] = "done"
    store.save(job)
    return {"id": job["id"], **table}


@router.post("/metadata/compare")
def compare_meta(payload: dict):
    a, b = payload.get("reference", {}), payload.get("moving", {})
    return {
        "sun_azimuth_difference": azimuth_difference_deg(a.get("sun_azimuth_deg"), b.get("sun_azimuth_deg")),
        "sun_elevation_difference": elevation_difference_deg(a.get("sun_elevation_deg"), b.get("sun_elevation_deg")),
        "gsd_ratio": (
            None
            if not a.get("gsd_m") or not b.get("gsd_m")
            else float(b["gsd_m"]) / float(a["gsd_m"])
        ),
    }
