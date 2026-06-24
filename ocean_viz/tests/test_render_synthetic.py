from pathlib import Path

import numpy as np
import xarray as xr
import yaml

from ocean_viz.animation import render_movie
from ocean_viz.plotting import render_snapshot


def _write_config(tmp_path: Path, data_path: Path) -> Path:
    cfg = {
        "dataset": {
            "name": "GLORYS12V1",
            "adapter": "glorys12",
            "access": {"type": "local", "path": str(data_path), "engine": "netcdf4"},
        },
        "region": {"name": "north_pacific", "lon_min": 160, "lon_max": 235, "lat_min": 40, "lat_max": 68},
        "time": {"start": "2018-06-01", "end": "2018-06-02", "timestep": "daily"},
        "variable": {
            "name": "sst",
            "source_var": "thetao",
            "display_name": "Sea surface temperature",
            "units": "degC",
            "surface_selector": {"mode": "top_layer"},
        },
        "derived": {"enabled": False},
        "visual": {
            "projection": "north_pacific_platecarree",
            "show_land": False,
            "show_coastline": False,
            "color_scale": {"vmin": 4, "vmax": 16, "cmap": "viridis", "units": "degC"},
        },
        "output": {
            "output_dir": str(tmp_path / "outputs"),
            "resolution": "720p",
            "dpi": 80,
            "snapshot": {"enabled": True, "date": "2018-06-01"},
            "movie": {"enabled": True, "fps": 2, "delete_frames": True},
        },
    }
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return cfg_path


def _write_dataset(tmp_path: Path) -> Path:
    data = xr.Dataset(
        {
            "thetao": (("time", "depth", "lat", "lon"), np.random.rand(2, 1, 3, 4) * 10 + 5),
        },
        coords={
            "time": np.array(["2018-06-01", "2018-06-02"], dtype="datetime64[ns]"),
            "depth": [0.5],
            "lat": [40.0, 54.0, 68.0],
            "lon": [160.0, 185.0, 210.0, 235.0],
        },
    )
    path = tmp_path / "sample.nc"
    data.to_netcdf(path)
    return path


def test_snapshot_and_movie_render(tmp_path: Path):
    data_path = _write_dataset(tmp_path)
    cfg_path = _write_config(tmp_path, data_path)

    png_path = Path(render_snapshot(cfg_path))
    mp4_path = Path(render_movie(cfg_path))

    assert png_path.exists() and png_path.suffix == ".png"
    assert mp4_path.exists() and mp4_path.suffix == ".mp4"
    assert not (Path(tmp_path) / "outputs" / "_frames").exists()
