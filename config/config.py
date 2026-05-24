import os
from dataclasses import dataclass
import tomllib
from dotenv import load_dotenv
from typing import Any, Self

load_dotenv()

class ConfigError(RuntimeError):
    pass

class Config:
    _FILE_PATH: str = './config/settings.toml'
    _instance: Self | None = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self.database_url = self._get_required("SUPABASE_URL")
        self._settings = self._load_from_file()
        self._initialized = True
    
    def _get_required(self, name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise ConfigError(f"Missing required environment variable: {name}")
        return value
    
    def _load_from_file(self) -> dict:
        try:
            with open(self._FILE_PATH, 'rb') as f:
                return tomllib.load(f)
        except FileNotFoundError:
            raise ConfigError(f"Configuration file not found: {self._FILE_PATH}")
        
    def get_env(self, name: str) -> str:
        return self._get_required(name)
        
    def get_config(self, *keys: str) -> dict:
        config = self._settings
        for key in keys:
            if key not in config:
                raise ConfigError(f"Missing configuration for: {'.'.join(keys)}")
            config = config[key]
        return config