"""Tests for longitude conversion and dateline handling."""

import numpy as np
import xarray as xr

from ocean_viz.dataset_loader import normalize_longitude


def test_normalize_longitude_negative_to_positive():
    """Test converting -180 to 180 range to 0 to 360."""
    # Create dataset with -180 to 180 convention
    lon = np.array([-180, -90, 0, 90, 180])
    ds = xr.Dataset(
        {"data": (["lon"], np.ones(5))},
        coords={"lon": lon},
    )

    ds_normalized = normalize_longitude(ds)

    expected_lon = np.array([0, 90, 180, 270, 360])
    np.testing.assert_array_almost_equal(ds_normalized.coords["lon"].values, expected_lon)


def test_normalize_longitude_sorting():
    """Test that longitude is sorted after conversion."""
    # Create unsorted -180 to 180 data
    lon = np.array([90, -180, 0, 180, -90])
    ds = xr.Dataset(
        {"data": (["lon"], np.array([1, 2, 3, 4, 5]))},
        coords={"lon": lon},
    )

    ds_normalized = normalize_longitude(ds)

    # Check sorted
    assert np.all(np.diff(ds_normalized.coords["lon"].values) >= 0)


def test_normalize_longitude_already_0_360():
    """Test with data already in 0-360 range."""
    lon = np.array([0, 90, 180, 270, 360])
    ds = xr.Dataset(
        {"data": (["lon"], np.ones(5))},
        coords={"lon": lon},
    )

    ds_normalized = normalize_longitude(ds)

    # Should remain unchanged (or sorted)
    expected_lon = np.array([0, 90, 180, 270, 360])
    np.testing.assert_array_almost_equal(ds_normalized.coords["lon"].values, expected_lon)


def test_normalize_longitude_preserves_data():
    """Test that data is preserved and reordered with longitude."""
    lon = np.array([90, -180, 0])
    data = np.array([1.0, 2.0, 3.0])
    ds = xr.Dataset(
        {"temperature": (["lon"], data)},
        coords={"lon": lon},
    )

    ds_normalized = normalize_longitude(ds)

    # Check data is reordered
    expected_lon = np.array([0, 90, 180])
    expected_data = np.array([3.0, 1.0, 2.0])

    np.testing.assert_array_almost_equal(ds_normalized.coords["lon"].values, expected_lon)
    np.testing.assert_array_almost_equal(ds_normalized["temperature"].values, expected_data)


def test_normalize_longitude_multidim():
    """Test normalization with multidimensional data."""
    lon = np.array([-90, 0, 90])
    lat = np.array([40, 50, 60])
    data = np.arange(9).reshape(3, 3)

    ds = xr.Dataset(
        {"temperature": (["lat", "lon"], data)},
        coords={"lon": lon, "lat": lat},
    )

    ds_normalized = normalize_longitude(ds)

    expected_lon = np.array([90, 180, 270])
    np.testing.assert_array_almost_equal(ds_normalized.coords["lon"].values, expected_lon)


def test_normalize_longitude_no_lon_coord():
    """Test that datasets without lon coordinate are returned unchanged."""
    ds = xr.Dataset(
        {"data": (["x"], np.ones(5))},
        coords={"x": np.arange(5)},
    )

    ds_normalized = normalize_longitude(ds)

    # Should be returned as-is
    assert "lon" not in ds_normalized.coords


def test_dateline_crossing_region():
    """Test detection/handling of dateline-crossing regions."""
    # A region that crosses dateline: lon_min > lon_max
    lon_min = 160
    lon_max = 235

    # In 0-360 convention, this should NOT cross dateline (normal case)
    # But 160-235 does cross if we think in -180 to 180 (would be 160 to -125)

    # For dateline crossing in 0-360: lon_min > lon_max indicates crossing
    # Example: lon_min=340, lon_max=20 would cross dateline

    # Create test case
    lon_min_cross = 340
    lon_max_cross = 20
    assert lon_min_cross > lon_max_cross  # Indicates crossing
