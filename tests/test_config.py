"""Tests for configuration loading and validation."""

import pytest
import tempfile
from pathlib import Path
import yaml

from ocean_viz.config import Config, load_config


def test_config_from_yaml():
    """Test loading config from YAML file."""
    config_dict = {
        "dataset": {"name": "test", "access": {"type": "local", "path": "*.nc"}},
        "region": {"lon_min": 0, "lon_max": 180, "lat_min": -90, "lat_max": 90},
        "time": {"start": "2020-01-01", "end": "2020-01-31"},
        "variable": {"name": "test_var", "source_var": "test_source"},
        "visual": {},
        "output": {},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_dict, f)
        temp_path = f.name

    try:
        config = Config.from_yaml(temp_path)
        assert config["dataset"]["name"] == "test"
        assert config.region["lon_min"] == 0
    finally:
        Path(temp_path).unlink()


def test_config_dict_like_access():
    """Test dict-like access to config."""
    config_dict = {"key": "value", "nested": {"inner": 123}}
    config = Config(config_dict)

    assert config["key"] == "value"
    assert config.get("nested")["inner"] == 123
    assert config.get("missing", "default") == "default"


def test_config_properties():
    """Test config property access."""
    config_dict = {
        "dataset": {"name": "test"},
        "region": {"lon_min": 0},
        "time": {"start": "2020-01-01"},
        "variable": {"name": "sst"},
        "visual": {"projection": "mercator"},
        "output": {"dpi": 200},
    }
    config = Config(config_dict)

    assert config.dataset["name"] == "test"
    assert config.region["lon_min"] == 0
    assert config.time["start"] == "2020-01-01"
    assert config.variable["name"] == "sst"
    assert config.visual["projection"] == "mercator"
    assert config.output["dpi"] == 200


def test_config_validation_required_sections():
    """Test that validation checks for required sections."""
    # Missing required section
    incomplete_config = {"dataset": {"name": "test"}}
    config = Config(incomplete_config)

    with pytest.raises(ValueError, match="Missing required section"):
        config.validate()


def test_config_validation_dataset_access():
    """Test validation of dataset access config."""
    config_dict = {
        "dataset": {"name": "test", "access": {"type": "local"}},  # missing path
        "region": {"lon_min": 0, "lon_max": 180, "lat_min": -90, "lat_max": 90},
        "time": {"start": "2020-01-01", "end": "2020-01-31"},
        "variable": {"name": "test_var", "source_var": "test_source"},
        "visual": {},
        "output": {},
    }
    config = Config(config_dict)

    with pytest.raises(ValueError, match="path"):
        config.validate()


def test_config_validation_region():
    """Test validation of region config."""
    config_dict = {
        "dataset": {"name": "test", "access": {"type": "local", "path": "*.nc"}},
        "region": {"lon_min": 0},  # missing required keys
        "time": {"start": "2020-01-01", "end": "2020-01-31"},
        "variable": {"name": "test_var", "source_var": "test_source"},
        "visual": {},
        "output": {},
    }
    config = Config(config_dict)

    with pytest.raises(ValueError, match="region"):
        config.validate()


def test_config_validation_time():
    """Test validation of time config."""
    config_dict = {
        "dataset": {"name": "test", "access": {"type": "local", "path": "*.nc"}},
        "region": {"lon_min": 0, "lon_max": 180, "lat_min": -90, "lat_max": 90},
        "time": {"start": "2020-01-01"},  # missing end
        "variable": {"name": "test_var", "source_var": "test_source"},
        "visual": {},
        "output": {},
    }
    config = Config(config_dict)

    with pytest.raises(ValueError, match="time"):
        config.validate()


def test_config_validation_variable():
    """Test validation of variable config."""
    config_dict = {
        "dataset": {"name": "test", "access": {"type": "local", "path": "*.nc"}},
        "region": {"lon_min": 0, "lon_max": 180, "lat_min": -90, "lat_max": 90},
        "time": {"start": "2020-01-01", "end": "2020-01-31"},
        "variable": {"name": "test_var"},  # missing source_var
        "visual": {},
        "output": {},
    }
    config = Config(config_dict)

    with pytest.raises(ValueError, match="variable"):
        config.validate()


def test_load_config():
    """Test load_config convenience function."""
    config_dict = {
        "dataset": {"name": "test", "access": {"type": "local", "path": "*.nc"}},
        "region": {"lon_min": 0, "lon_max": 180, "lat_min": -90, "lat_max": 90},
        "time": {"start": "2020-01-01", "end": "2020-01-31"},
        "variable": {"name": "test_var", "source_var": "test_source"},
        "visual": {},
        "output": {},
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_dict, f)
        temp_path = f.name

    try:
        config = load_config(temp_path)
        assert isinstance(config, Config)
        assert config.dataset["name"] == "test"
    finally:
        Path(temp_path).unlink()
