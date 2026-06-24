import numpy as np
import xarray as xr

from ocean_viz.derived import current_speed, thermal_habitat_mask


def test_current_speed_calculation():
    u = xr.DataArray(np.array([[3.0, 4.0]]), dims=["lat", "lon"])
    v = xr.DataArray(np.array([[4.0, 3.0]]), dims=["lat", "lon"])
    out = current_speed(u, v)
    assert out.values.tolist() == [[5.0, 5.0]]


def test_thermal_habitat_mask():
    sst = xr.DataArray(np.array([[6.0, 12.0, 16.0]]), dims=["lat", "lon"])
    mask = thermal_habitat_mask(sst, 5, 15)
    assert mask.values.tolist() == [[True, True, False]]
