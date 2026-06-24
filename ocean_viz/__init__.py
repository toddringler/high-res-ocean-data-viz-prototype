"""Ocean visualization package for GLORYS12V1 reanalysis data."""

__version__ = "0.1.0"

from ocean_viz.config import Config, load_config
from ocean_viz.dataset_loader import load_ocean_data
from ocean_viz.plotting import render_snapshot
from ocean_viz.animation import render_movie

__all__ = [
    "Config",
    "load_config",
    "load_ocean_data",
    "render_snapshot",
    "render_movie",
]
