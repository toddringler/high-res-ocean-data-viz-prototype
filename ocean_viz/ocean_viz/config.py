from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Raised for invalid configuration."""


def load_config(config_path: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(config_path, dict):
        config = config_path
    else:
        with Path(config_path).open("r", encoding="utf-8") as fh:
            config = yaml.safe_load(fh) or {}
    return validate_config(config)


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    required = ["dataset", "region", "time", "variable", "visual", "output"]
    missing = [name for name in required if name not in config]
    if missing:
        raise ConfigError(f"Missing required config sections: {', '.join(missing)}")
    if config["time"].get("timestep") != "daily":
        raise ConfigError("Version 1 supports only daily timestep")
    return config
