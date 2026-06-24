import numpy as np
import xarray as xr

from ocean_viz.dataset_loader import subset_region, to_360


def test_to_360_conversion():
    lon = xr.DataArray(np.array([-170, 0, 10]))
    converted = to_360(lon)
    assert converted.values.tolist() == [190, 0, 10]


def test_dateline_safe_region_selection():
    ds = xr.Dataset(
        {"var": (("lat", "lon"), np.arange(12).reshape(3, 4))},
        coords={"lat": [40, 50, 60], "lon": [170, 200, 300, 350]},
    )
    out = subset_region(ds, lon_min=300, lon_max=30, lat_min=40, lat_max=60)
    assert out.lon.min() >= 0
    assert 300 in out.lon.values
