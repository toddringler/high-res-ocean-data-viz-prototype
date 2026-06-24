from __future__ import annotations

import numpy as np
import xarray as xr


def current_speed(u_current: xr.DataArray, v_current: xr.DataArray) -> xr.DataArray:
    speed = np.hypot(u_current, v_current)
    speed.name = "current_speed"
    speed.attrs["units"] = "m/s"
    return speed


def sst_gradient_strength(sst: xr.DataArray) -> xr.DataArray:
    ddy = sst.differentiate("lat")
    ddx = sst.differentiate("lon")
    out = np.hypot(ddx, ddy)
    out.name = "sst_gradient_strength"
    return out


def sst_anomaly(sst: xr.DataArray, baseline: xr.DataArray | None = None) -> xr.DataArray:
    base = baseline if baseline is not None else sst.mean("time")
    out = sst - base
    out.name = "sst_anomaly"
    return out


def thermal_habitat_mask(sst: xr.DataArray, min_temp: float, max_temp: float) -> xr.DataArray:
    mask = (sst >= min_temp) & (sst <= max_temp)
    mask.name = "thermal_habitat_mask"
    return mask
