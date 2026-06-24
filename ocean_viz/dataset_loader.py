"""Data loading and preprocessing."""

import xarray as xr
import numpy as np
from typing import Dict, Any, Tuple, Optional
from datetime import date, datetime, time

from ocean_viz.config import Config
from ocean_viz.dataset_adapters import get_adapter
from ocean_viz.variables import get_variable_metadata, is_3d_variable


def _parse_time_value(value: Any, field_name: str) -> datetime:
    """Parse config time values from YAML into timezone-naive datetime.

    YAML may deserialize ISO-like values into ``date`` objects, not strings.
    This helper accepts str/date/datetime and normalizes to ``datetime``.
    """
    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, time.min)

    if isinstance(value, str):
        return datetime.fromisoformat(value)

    raise TypeError(
        f"Invalid type for time.{field_name}: expected str/date/datetime, got {type(value).__name__}"
    )


def normalize_longitude(ds: xr.Dataset) -> xr.Dataset:
    """Convert longitude to 0-360 range."""
    if "lon" not in ds.coords:
        return ds

    lon = ds.coords["lon"].values.astype(float)

    # For monotonic [-180, 180] grids, shift by +180 to produce [0, 360].
    # For unsorted or mixed inputs, fallback to wrapping only negative values.
    lon_min = np.nanmin(lon)
    lon_max = np.nanmax(lon)
    is_monotonic = np.all(np.diff(lon) >= 0)

    if lon_min < 0 and lon_max <= 180 and is_monotonic:
        lon = lon + 180
    else:
        lon = np.where(lon < 0, lon + 360, lon)

    # Sort by longitude
    sort_idx = np.argsort(lon)
    lon = lon[sort_idx]

    # Create new dataset with normalized longitude
    ds = ds.isel(lon=sort_idx)
    ds.coords["lon"] = lon

    return ds


def extract_surface_layer(
    ds: xr.Dataset, var_name: str, surface_config: Dict[str, Any]
) -> xr.DataArray:
    """Extract surface layer from 3D variable according to config.
    
    surface_config should contain:
    - mode: 'top_layer', 'nearest_depth', or 'depth_index'
    - depth_m: target depth (for nearest_depth mode)
    - depth_idx: depth index (for depth_index mode)
    """
    if var_name not in ds.data_vars:
        available = ", ".join(ds.data_vars)
        raise ValueError(
            f"Variable '{var_name}' not found in dataset. Available: {available}"
        )

    data = ds[var_name]

    # Check if variable has depth dimension
    depth_dims = [d for d in ["depth", "z", "lev", "level"] if d in data.dims]

    if not depth_dims:
        # No depth dimension, return as-is
        return data

    depth_dim = depth_dims[0]

    mode = surface_config.get("mode", "top_layer")

    if mode == "top_layer":
        # Take first depth level
        return data.isel({depth_dim: 0})

    elif mode == "nearest_depth":
        target_depth = surface_config.get("depth_m", 0)
        depth_coord = ds.coords[depth_dim]

        # Find nearest depth
        depth_idx = np.argmin(np.abs(depth_coord.values - target_depth))
        return data.isel({depth_dim: depth_idx})

    elif mode == "depth_index":
        depth_idx = surface_config.get("depth_idx", 0)
        return data.isel({depth_dim: depth_idx})

    else:
        raise ValueError(f"Unknown surface selector mode: {mode}")


def load_ocean_data(config_path: str) -> xr.Dataset:
    """Load ocean data from configuration file.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        xarray Dataset with loaded and preprocessed data
    """
    from ocean_viz.config import load_config

    config = load_config(config_path)

    # Get adapter
    adapter = get_adapter(config.dataset)

    # Parse time range
    time_start = _parse_time_value(config.time["start"], "start")
    time_end = _parse_time_value(config.time["end"], "end")

    # Get region bounds (assumes 0-360 convention already)
    region = config.region
    lon_min = region["lon_min"]
    lon_max = region["lon_max"]
    lat_min = region["lat_min"]
    lat_max = region["lat_max"]

    # Load dataset
    ds = adapter.open_dataset(
        lon_range=(lon_min, lon_max),
        lat_range=(lat_min, lat_max),
        time_range=(time_start, time_end),
    )

    # Normalize longitude to 0-360
    ds = normalize_longitude(ds)

    # Extract surface layer for the requested variable
    var_config = config.variable
    var_name = var_config.get("source_var")

    if is_3d_variable(var_config["name"]):
        surface_config = var_config.get("surface_selector", {"mode": "top_layer"})
        data = extract_surface_layer(ds, var_name, surface_config)
    else:
        if var_name not in ds.data_vars:
            available = ", ".join(ds.data_vars)
            raise ValueError(
                f"Variable '{var_name}' not found in dataset. Available: {available}"
            )
        data = ds[var_name]

    # Return as dataset with renamed variable
    return data.to_dataset(name=var_config["name"])


def load_ocean_data_raw(config_path: str) -> xr.Dataset:
    """Load raw ocean data without surface extraction for derived variables."""
    from ocean_viz.config import load_config

    config = load_config(config_path)

    adapter = get_adapter(config.dataset)

    time_start = _parse_time_value(config.time["start"], "start")
    time_end = _parse_time_value(config.time["end"], "end")

    region = config.region
    lon_min = region["lon_min"]
    lon_max = region["lon_max"]
    lat_min = region["lat_min"]
    lat_max = region["lat_max"]

    ds = adapter.open_dataset(
        lon_range=(lon_min, lon_max),
        lat_range=(lat_min, lat_max),
        time_range=(time_start, time_end),
    )

    ds = normalize_longitude(ds)

    return ds
