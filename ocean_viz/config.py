"""Configuration loading and validation."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration container for ocean visualization."""

    def __init__(self, config_dict: Dict[str, Any]):
        """Initialize from dictionary."""
        self._config = config_dict

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Config":
        """Load configuration from YAML file."""
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"Config file not found: {yaml_path}")

        with open(yaml_path, "r") as f:
            config_dict = yaml.safe_load(f)

        if config_dict is None:
            raise ValueError(f"Empty config file: {yaml_path}")

        return cls(config_dict)

    def __getitem__(self, key: str) -> Any:
        """Dict-like access."""
        return self._config[key]

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like get."""
        return self._config.get(key, default)

    @property
    def project(self) -> Dict[str, Any]:
        return self._config.get("project", {})

    @property
    def dataset(self) -> Dict[str, Any]:
        return self._config.get("dataset", {})

    @property
    def region(self) -> Dict[str, Any]:
        return self._config.get("region", {})

    @property
    def time(self) -> Dict[str, Any]:
        return self._config.get("time", {})

    @property
    def variable(self) -> Dict[str, Any]:
        return self._config.get("variable", {})

    @property
    def derived(self) -> Dict[str, Any]:
        return self._config.get("derived", {})

    @property
    def visual(self) -> Dict[str, Any]:
        return self._config.get("visual", {})

    @property
    def habitat_bands(self) -> Dict[str, Any]:
        return self._config.get("habitat_bands", {})

    @property
    def output(self) -> Dict[str, Any]:
        return self._config.get("output", {})

    def validate(self) -> bool:
        """Validate configuration structure."""
        required_sections = ["dataset", "region", "time", "variable", "visual", "output"]
        for section in required_sections:
            if section not in self._config:
                raise ValueError(f"Missing required section: {section}")

        # Validate dataset section
        dataset = self.dataset
        if "access" not in dataset:
            raise ValueError("Missing dataset.access")
        if dataset["access"].get("type") == "local" and "path" not in dataset["access"]:
            raise ValueError("Missing dataset.access.path for local access")

        # Validate region section
        region = self.region
        required_region_keys = ["lon_min", "lon_max", "lat_min", "lat_max"]
        for key in required_region_keys:
            if key not in region:
                raise ValueError(f"Missing region.{key}")

        # Validate time section
        time_cfg = self.time
        if "start" not in time_cfg or "end" not in time_cfg:
            raise ValueError("Missing time.start or time.end")

        # Validate variable section
        var = self.variable
        if "name" not in var or "source_var" not in var:
            raise ValueError("Missing variable.name or variable.source_var")

        return True


def load_config(config_path: str) -> Config:
    """Load and validate configuration from YAML file."""
    config = Config.from_yaml(config_path)
    config.validate()
    return config
