from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "processed"


class JobStore:
    def __init__(self):
        DATA.mkdir(parents=True, exist_ok=True)
        self.jobs: dict[str, dict[str, Any]] = {}

    def create(self) -> dict:
        jid = uuid.uuid4().hex[:12]
        d = DATA / jid
        d.mkdir(parents=True, exist_ok=True)
        job = {
            "id": jid,
            "status": "created",
            "dir": str(d),
            "stage": "created",
            "result": None,
            "error": None,
        }
        self.jobs[jid] = job
        return job

    def get(self, jid: str) -> Optional[dict]:
        if jid in self.jobs:
            return self.jobs[jid]
        p = DATA / jid / "job.json"
        if p.exists():
            job = json.loads(p.read_text(encoding="utf-8"))
            self.jobs[jid] = job
            return job
        return None

    def save(self, job: dict) -> None:
        self.jobs[job["id"]] = job
        path = Path(job["dir"]) / "job.json"
        slim = {k: v for k, v in job.items() if k != "result" or True}
        # keep result; files can be large but OK for demo scale
        path.write_text(json.dumps(slim, default=str), encoding="utf-8")


store = JobStore()
