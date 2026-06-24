from pathlib import Path

import pytest

from ocean_viz.config import ConfigError, load_config


def test_load_config_valid():
    cfg = load_config("configs/glorys12_sst_demo.yaml")
    assert cfg["dataset"]["name"] == "GLORYS12V1"


def test_load_config_missing_required(tmp_path: Path):
    path = tmp_path / "bad.yaml"
    path.write_text("dataset: {}\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)
