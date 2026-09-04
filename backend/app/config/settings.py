from __future__ import annotations

from pathlib import Path

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    random_seed: int = 42
    host: str = "127.0.0.1"
    port: int = 8000

    class Config:
        env_prefix = "LUNAALIGN_"


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_yaml() -> dict:
    p = project_root() / "configs" / "default.yaml"
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


settings = Settings()
