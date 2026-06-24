from __future__ import annotations

from pathlib import Path

import numpy as np
import xarray as xr

from .config import load_config
from .dataset_adapters import list_available_variables, normalize_coords
from .derived import current_speed, sst_anomaly, sst_gradient_strength, thermal_habitat_mask
from .variables import select_surface


class DatasetError(ValueError):
    """Raised for dataset access errors."""


def to_360(longitude: xr.DataArray) -> xr.DataArray:
    return (longitude % 360 + 360) % 360


def subset_region(da: xr.DataArray | xr.Dataset, lon_min: float, lon_max: float, lat_min: float, lat_max: float):
    target = da.sel(lat=slice(lat_min, lat_max))
    if lon_min <= lon_max:
        return target.sel(lon=slice(lon_min, lon_max))
    left = target.sel(lon=slice(lon_min, 360))
    right = target.sel(lon=slice(0, lon_max))
    return xr.concat([left, right], dim="lon").sortby("lon")


def _open_dataset(access_cfg: dict) -> xr.Dataset:
    source_path = access_cfg.get("path")
    if not source_path:
        raise DatasetError("dataset.access.path is required")
    access_type = access_cfg.get("type", "local")
    if access_type != "local":
        raise DatasetError("Version 1 supports only local access")
    engine = access_cfg.get("engine")
    if str(source_path).endswith(".zarr"):
        return xr.open_zarr(source_path)
    return xr.open_mfdataset(source_path, combine="by_coords", engine=engine, chunks={})


def _resolve_variable(ds: xr.Dataset, cfg: dict) -> xr.DataArray:
    variable_cfg = cfg["variable"]
    source_var = variable_cfg.get("source_var")
    if source_var not in ds.data_vars:
        available = ", ".join(list_available_variables(ds))
        raise DatasetError(
            f"Requested variable '{source_var}' not found. Available variables: {available}"
        )
    return select_surface(ds[source_var], variable_cfg.get("surface_selector"))


def _apply_derived(da: xr.DataArray, ds: xr.Dataset, cfg: dict) -> xr.DataArray:
    derived_cfg = cfg.get("derived", {})
    if not derived_cfg.get("enabled"):
        return da
    name = derived_cfg.get("name")
    if name == "current_speed":
        return current_speed(ds[derived_cfg["u_var"]], ds[derived_cfg["v_var"]])
    if name == "sst_gradient_strength":
        return sst_gradient_strength(da)
    if name == "sst_anomaly":
        return sst_anomaly(da)
    if name == "thermal_habitat_mask":
        band = derived_cfg.get("band", {})
        return thermal_habitat_mask(da, float(band["min"]), float(band["max"]))
    raise DatasetError(f"Unsupported derived variable: {name}")


def load_ocean_data(config_path: str | Path | dict) -> xr.DataArray:
    cfg = load_config(config_path)
    ds = _open_dataset(cfg["dataset"]["access"])
    ds = normalize_coords(ds)
    if "lon" not in ds.coords or "lat" not in ds.coords or "time" not in ds.coords:
        raise DatasetError("Dataset must include time, lat, and lon coordinates")
    ds = ds.assign_coords(lon=to_360(ds["lon"])).sortby("lon")

    time_cfg = cfg["time"]
    ds = ds.sel(time=slice(time_cfg["start"], time_cfg["end"]))

    region = cfg["region"]
    ds = subset_region(ds, region["lon_min"], region["lon_max"], region["lat_min"], region["lat_max"])

    da = _resolve_variable(ds, cfg)
    da = _apply_derived(da, ds, cfg)

    if da.attrs.get("units") is None and cfg["variable"].get("units"):
        da.attrs["units"] = cfg["variable"]["units"]
    da.name = cfg["variable"].get("name", da.name)
    return da
