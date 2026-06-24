from __future__ import annotations

from pathlib import Path
import shutil

import imageio.v2 as imageio

from .config import load_config
from .dataset_loader import load_ocean_data
from .plotting import auto_filename, render_dataarray_map


def render_movie(config_path: str | Path | dict) -> str:
    cfg = load_config(config_path)
    da = load_ocean_data(cfg)
    out_cfg = cfg["output"]
    movie_cfg = out_cfg.get("movie", {})

    out_dir = Path(out_cfg.get("output_dir", "outputs"))
    out_dir.mkdir(parents=True, exist_ok=True)
    frame_dir = out_dir / "_frames"
    frame_dir.mkdir(parents=True, exist_ok=True)

    times = da["time"].values
    if len(times) == 0:
        raise ValueError("No timesteps available for requested range")

    color_scale = cfg["visual"].get("color_scale", {})
    frame_paths: list[Path] = []
    for idx, ts in enumerate(times):
        frame_path = frame_dir / f"frame_{idx:04d}.png"
        render_dataarray_map(da.sel(time=ts), cfg, ts, frame_path, color_scale)
        frame_paths.append(frame_path)

    date_start = str(times[0])[:10].replace("-", "")
    date_end = str(times[-1])[:10].replace("-", "")
    filename = auto_filename(cfg, "movie", f"{date_start}-{date_end}") + ".mp4"
    movie_path = out_dir / filename

    with imageio.get_writer(movie_path, fps=movie_cfg.get("fps", 4), codec="libx264") as writer:
        for frame in frame_paths:
            writer.append_data(imageio.imread(frame))

    if movie_cfg.get("delete_frames", True):
        shutil.rmtree(frame_dir, ignore_errors=True)
    return str(movie_path)
