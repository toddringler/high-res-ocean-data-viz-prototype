from __future__ import annotations

import xarray as xr


class VariableSelectionError(ValueError):
    """Raised when variable/surface selection fails."""


def select_surface(da: xr.DataArray, selector: dict | None) -> xr.DataArray:
    if selector is None or "depth" not in da.dims:
        return da
    mode = selector.get("mode", "top_layer")
    if mode == "top_layer":
        return da.isel(depth=0)
    if mode == "nearest_depth":
        return da.sel(depth=float(selector.get("depth_m", 0.0)), method="nearest")
    if mode == "depth_index":
        return da.isel(depth=int(selector.get("index", 0)))
    raise VariableSelectionError(f"Unsupported surface selector mode: {mode}")
