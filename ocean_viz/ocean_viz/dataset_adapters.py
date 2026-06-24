from __future__ import annotations

from typing import Iterable

import xarray as xr

COORD_ALIASES = {
    "time": ("time", "TIME"),
    "lat": ("lat", "latitude", "nav_lat"),
    "lon": ("lon", "longitude", "nav_lon"),
    "depth": ("depth", "deptht", "lev", "z"),
}


def normalize_coords(ds: xr.Dataset) -> xr.Dataset:
    rename_map: dict[str, str] = {}
    for canonical, aliases in COORD_ALIASES.items():
        for alias in aliases:
            if alias in ds.coords and alias != canonical:
                rename_map[alias] = canonical
                break
    return ds.rename(rename_map) if rename_map else ds


def list_available_variables(ds: xr.Dataset, skip: Iterable[str] = ("time", "lat", "lon", "depth")) -> list[str]:
    return sorted([v for v in ds.data_vars if v not in set(skip)])
