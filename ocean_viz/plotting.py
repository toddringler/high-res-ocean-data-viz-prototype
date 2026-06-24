"""Map rendering with matplotlib and cartopy."""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import date as date_type, datetime, time

from ocean_viz.config import Config
from ocean_viz.variables import get_variable_metadata


def _parse_render_date(value: object) -> datetime:
    """Parse render date from config or argument into datetime."""
    if isinstance(value, datetime):
        return value

    if isinstance(value, date_type):
        return datetime.combine(value, time.min)

    if isinstance(value, str):
        return datetime.fromisoformat(value)

    raise TypeError(
        f"Invalid date value type: expected str/date/datetime, got {type(value).__name__}"
    )


def get_projection(projection_name: str) -> ccrs.Projection:
    """Get cartopy projection."""
    projections = {
        "north_pacific_platecarree": ccrs.PlateCarree(central_longitude=200),
        "platecarree": ccrs.PlateCarree(),
        "mercator": ccrs.Mercator(),
        "orthographic": ccrs.Orthographic(central_longitude=200, central_latitude=50),
    }

    proj = projections.get(projection_name.lower())
    if proj is None:
        return ccrs.PlateCarree(central_longitude=200)

    return proj


def render_snapshot(config_path: str, date: Optional[str] = None) -> str:
    """Render a single snapshot PNG.
    
    Args:
        config_path: Path to config file
        date: Date to render (ISO format), uses config default if not provided
        
    Returns:
        Path to output PNG file
    """
    from ocean_viz.config import load_config
    from ocean_viz.dataset_loader import load_ocean_data

    config = load_config(config_path)

    # Load data
    ds = load_ocean_data(config_path)

    # Select date
    if date is None:
        date = config.output.get("snapshot", {}).get("date")
        if date is None:
            date = config.time["start"]

    # Parse date and select
    date_obj = _parse_render_date(date)
    data = ds.sel(time=date_obj, method="nearest")

    var_name = config.variable["name"]
    var_data = data[var_name]

    # Get visualization config
    visual = config.visual
    color_scale = visual.get("color_scale", {})
    vmin = color_scale.get("vmin")
    vmax = color_scale.get("vmax")
    cmap = color_scale.get("cmap", "turbo")

    # Get defaults if not provided
    if vmin is None or vmax is None:
        var_meta = get_variable_metadata(var_name)
        if vmin is None:
            vmin = var_meta.get("vmin", 0)
        if vmax is None:
            vmax = var_meta.get("vmax", 1)

    # Create figure
    projection = get_projection(visual.get("projection", "north_pacific_platecarree"))
    transform = ccrs.PlateCarree()

    fig = plt.figure(figsize=(12, 8), dpi=100)
    ax = plt.axes(projection=projection)

    # Plot data
    im = ax.contourf(
        var_data.lon,
        var_data.lat,
        var_data,
        transform=transform,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        levels=20,
    )

    # Add features
    if visual.get("show_land", True):
        ax.add_feature(cfeature.LAND, facecolor="lightgray")
    if visual.get("show_coastline", True):
        ax.add_feature(cfeature.COASTLINE, edgecolor="black", linewidth=0.5)

    # Set extent
    region = config.region
    extent = [region["lon_min"], region["lon_max"], region["lat_min"], region["lat_max"]]
    ax.set_extent(extent, crs=transform)

    # Colorbar
    cbar = plt.colorbar(
        im, ax=ax, orientation="horizontal", pad=0.05, shrink=0.8, aspect=40
    )
    var_meta = get_variable_metadata(var_name)
    cbar.set_label(f"{var_meta.get('display_name', var_name)} ({var_meta.get('units', '')})")

    # Title
    date_str = date_obj.strftime("%Y-%m-%d")
    title = f"{config.dataset.get('name', 'Dataset')} - {var_meta.get('display_name', var_name)}\n{date_str}"
    ax.set_title(title, fontsize=14, fontweight="bold")

    # Generate output filename
    output_dir = Path(config.output.get("output_dir", "outputs"))
    output_dir.mkdir(parents=True, exist_ok=True)

    region_name = config.region.get("name", "region")
    dataset_name = config.dataset.get("name", "data").lower().replace(" ", "_")
    var_short = var_name.lower().replace(" ", "_")

    filename = (
        f"{dataset_name}_{var_short}_{date_obj.strftime('%Y%m%d')}"
        f"_{region_name}_snapshot.png"
    )
    output_path = output_dir / filename

    # Save
    plt.savefig(output_path, dpi=config.output.get("dpi", 200), bbox_inches="tight")
    plt.close()

    return str(output_path)


def render_frame(
    data: xr.DataArray,
    config: Config,
    date: datetime,
    vmin: float = None,
    vmax: float = None,
    cmap: str = "turbo",
) -> Tuple[plt.Figure, plt.Axes]:
    """Render a single frame for animation.
    
    Args:
        data: Data array to plot
        config: Configuration object
        date: Date of frame
        vmin, vmax: Color scale limits
        cmap: Colormap name
        
    Returns:
        (figure, axes) tuple
    """
    projection = get_projection(config.visual.get("projection", "north_pacific_platecarree"))
    transform = ccrs.PlateCarree()

    fig = plt.figure(figsize=(12, 8), dpi=100)
    ax = plt.axes(projection=projection)

    # Plot
    im = ax.contourf(
        data.lon,
        data.lat,
        data,
        transform=transform,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        levels=20,
    )

    # Features
    if config.visual.get("show_land", True):
        ax.add_feature(cfeature.LAND, facecolor="lightgray")
    if config.visual.get("show_coastline", True):
        ax.add_feature(cfeature.COASTLINE, edgecolor="black", linewidth=0.5)

    # Extent
    region = config.region
    extent = [region["lon_min"], region["lon_max"], region["lat_min"], region["lat_max"]]
    ax.set_extent(extent, crs=transform)

    # Colorbar
    cbar = plt.colorbar(
        im, ax=ax, orientation="horizontal", pad=0.05, shrink=0.8, aspect=40
    )
    var_name = config.variable["name"]
    var_meta = get_variable_metadata(var_name)
    cbar.set_label(f"{var_meta.get('display_name')} ({var_meta.get('units')})")

    # Title
    date_str = date.strftime("%Y-%m-%d")
    title = f"{config.dataset.get('name')} - {var_meta.get('display_name')}\n{date_str}"
    ax.set_title(title, fontsize=14, fontweight="bold")

    return fig, ax
