import os
from dataclasses import dataclass


class ConfigError(RuntimeError):
    pass

class Config:
    def __init__(self):
        self.database_url = _get_required("DATABASE_URL")
        self.debug = _to_bool(os.getenv("DEBUG"), default=False)

def _get_required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ConfigError(f"Missing required environment variable: {name}")
    return value


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

