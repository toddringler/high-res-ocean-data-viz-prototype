import numpy as np
import xarray as xr

from ocean_viz.variables import select_surface


def test_surface_selector_top_layer_and_nearest_depth():
    da = xr.DataArray(
        np.arange(12).reshape(3, 2, 2),
        dims=["depth", "lat", "lon"],
        coords={"depth": [0.5, 5.0, 20.0], "lat": [0, 1], "lon": [0, 1]},
    )
    top = select_surface(da, {"mode": "top_layer"})
    near = select_surface(da, {"mode": "nearest_depth", "depth_m": 4.0})
    assert "depth" not in top.dims
    assert near.equals(da.isel(depth=1))
