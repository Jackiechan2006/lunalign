from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.routes import router

app = FastAPI(
    title="LunaAlign-X",
    description=(
        "Multi-modal lunar image correspondence for Chandrayaan-2 OHRC, TMC-2 and IIRS. "
        "Classical computer vision core; optional deep-learning adapters; no automatic downloads."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

data_dir = Path(__file__).resolve().parents[3] / "data"
data_dir.mkdir(parents=True, exist_ok=True)


@app.get("/")
def root():
    return {
        "name": "LunaAlign-X",
        "subtitle": "Multi-Modal, Sun-Angle and Scale-Invariant Lunar Image Correspondence",
        "core": "offline classical computer vision",
        "docs": "/docs",
    }
