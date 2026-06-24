"""Animation and MP4 rendering."""

import numpy as np
import matplotlib.pyplot as plt
import imageio
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import tempfile
import os

from ocean_viz.config import load_config
from ocean_viz.dataset_loader import load_ocean_data
from ocean_viz.variables import get_variable_metadata
from ocean_viz.plotting import render_frame


def render_movie(config_path: str, fps: Optional[int] = None) -> str:
    """Render MP4 movie from daily data.
    
    Args:
        config_path: Path to config file
        fps: Frames per second (uses config default if not provided)
        
    Returns:
        Path to output MP4 file
    """
    config = load_config(config_path)

    # Load data
    ds = load_ocean_data(config_path)

    # Get FPS
    if fps is None:
        fps = config.output.get("movie", {}).get("fps", 4)

    # Get color scale
    visual = config.visual
    color_scale = visual.get("color_scale", {})
    vmin = color_scale.get("vmin")
    vmax = color_scale.get("vmax")
    cmap = color_scale.get("cmap", "turbo")

    # Get defaults if not provided
    if vmin is None or vmax is None:
        var_name = config.variable["name"]
        var_meta = get_variable_metadata(var_name)
        if vmin is None:
            vmin = var_meta.get("vmin", 0)
        if vmax is None:
            vmax = var_meta.get("vmax", 1)

    # Create temporary directory for frames
    with tempfile.TemporaryDirectory() as tmpdir:
        frame_dir = Path(tmpdir)

        # Render frames
        var_name = config.variable["name"]
        times = ds.time.values

        frame_files = []
        for i, time_val in enumerate(times):
            # Select timestep
            data = ds.isel(time=i)[var_name]

            # Convert numpy datetime64 to datetime
            time_obj = datetime.utcfromtimestamp(
                (time_val - np.datetime64(0, "s")) / np.timedelta64(1, "s")
            )

            # Render frame
            fig, ax = render_frame(
                data, config, time_obj, vmin=vmin, vmax=vmax, cmap=cmap
            )

            # Save frame
            frame_file = frame_dir / f"frame_{i:04d}.png"
            fig.savefig(frame_file, dpi=config.output.get("dpi", 200), bbox_inches="tight")
            plt.close(fig)

            frame_files.append(str(frame_file))

            # Progress
            if (i + 1) % 10 == 0:
                print(f"Rendered {i + 1}/{len(times)} frames")

        # Create MP4
        output_dir = Path(config.output.get("output_dir", "outputs"))
        output_dir.mkdir(parents=True, exist_ok=True)

        region_name = config.region.get("name", "region")
        dataset_name = config.dataset.get("name", "data").lower().replace(" ", "_")
        var_short = var_name.lower().replace(" ", "_")

        time_start = config.time["start"]
        time_end = config.time["end"]

        filename = (
            f"{dataset_name}_{var_short}_{time_start.replace('-', '')}"
            f"-{time_end.replace('-', '')}_{region_name}_movie.mp4"
        )
        output_path = output_dir / filename

        # Write MP4
        print(f"Writing MP4 to {output_path}...")
        writer = imageio.get_writer(str(output_path), fps=fps)

        for frame_file in frame_files:
            img = imageio.imread(frame_file)
            writer.append_data(img)

        writer.close()
        print(f"Movie created: {output_path}")

        # Delete frame files if configured
        if config.output.get("movie", {}).get("delete_frames", True):
            for frame_file in frame_files:
                os.remove(frame_file)

    return str(output_path)
