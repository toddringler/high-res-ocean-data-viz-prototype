"""Tests for derived variables."""

import numpy as np
import xarray as xr

from ocean_viz.derived import (
    calculate_current_speed,
    calculate_sst_gradient,
    calculate_sst_anomaly,
    calculate_thermal_habitat_mask,
)


def create_test_dataset():
    """Create synthetic test dataset."""
    np.random.seed(42)
    lon = np.linspace(160, 235, 10)
    lat = np.linspace(40, 68, 8)
    time = np.arange(5)

    u_data = np.random.rand(5, 8, 10) * 0.5 - 0.25
    v_data = np.random.rand(5, 8, 10) * 0.5 - 0.25
    sst_data = np.random.rand(5, 8, 10) * 10 + 5

    return xr.Dataset(
        {
            "uo": (["time", "lat", "lon"], u_data),
            "vo": (["time", "lat", "lon"], v_data),
            "thetao": (["time", "lat", "lon"], sst_data),
        },
        coords={"time": time, "lat": lat, "lon": lon},
    )


def test_current_speed_calculation():
    """Test current speed calculation."""
    ds = create_test_dataset()

    speed = calculate_current_speed(ds)

    # Speed should be sqrt(u^2 + v^2)
    u = ds["uo"].values
    v = ds["vo"].values
    expected_speed = np.sqrt(u**2 + v**2)

    np.testing.assert_array_almost_equal(speed.values, expected_speed)


def test_current_speed_shape():
    """Test that current speed has same shape as input components."""
    ds = create_test_dataset()

    speed = calculate_current_speed(ds)

    assert speed.shape == ds["uo"].shape


def test_current_speed_always_positive():
    """Test that current speed is always non-negative."""
    ds = create_test_dataset()

    speed = calculate_current_speed(ds)

    assert np.all(speed.values >= 0)


def test_current_speed_missing_variable():
    """Test error when required variable is missing."""
    ds = xr.Dataset(
        {"uo": (["time", "lat", "lon"], np.random.rand(5, 8, 10))},
        coords={"time": np.arange(5), "lat": np.arange(8), "lon": np.arange(10)},
    )

    with np.testing.assert_raises(ValueError):
        calculate_current_speed(ds)


def test_sst_anomaly_zero_mean():
    """Test that SST anomaly has zero temporal mean."""
    ds = create_test_dataset()

    anomaly = calculate_sst_anomaly(ds)

    # Temporal mean should be ~0
    temporal_mean = float(anomaly.mean(dim="time").mean())
    assert abs(temporal_mean) < 1e-6


def test_sst_anomaly_shape():
    """Test that SST anomaly has same shape as input."""
    ds = create_test_dataset()

    anomaly = calculate_sst_anomaly(ds)

    assert anomaly.shape == ds["thetao"].shape


def test_sst_anomaly_bounds():
    """Test that SST anomaly is bounded by data range."""
    ds = create_test_dataset()

    anomaly = calculate_sst_anomaly(ds)

    # Anomaly should be bounded by range of input
    data_range = float(ds["thetao"].max() - ds["thetao"].min())
    assert float(anomaly.max()) <= data_range + 1e-6
    assert float(anomaly.min()) >= -data_range - 1e-6


def test_thermal_habitat_mask_binary():
    """Test that thermal habitat mask is binary (0 or 1)."""
    ds = create_test_dataset()

    mask = calculate_thermal_habitat_mask(ds, temp_min=5, temp_max=15)

    unique_values = np.unique(mask.values)
    assert set(unique_values).issubset({0.0, 1.0})


def test_thermal_habitat_mask_correct_range():
    """Test that mask correctly identifies temperature range."""
    ds = create_test_dataset()

    mask = calculate_thermal_habitat_mask(ds, temp_min=8, temp_max=12)

    sst = ds["thetao"]

    # Where mask is 1, SST should be in range
    in_mask = sst.values[mask.values > 0.5]
    if len(in_mask) > 0:
        assert np.all(in_mask >= 8)
        assert np.all(in_mask <= 12)

    # Where mask is 0, SST should be out of range
    out_mask = sst.values[mask.values < 0.5]
    if len(out_mask) > 0:
        assert np.any((out_mask < 8) | (out_mask > 12))


def test_thermal_habitat_mask_narrow_range():
    """Test mask with narrow temperature range."""
    ds = create_test_dataset()

    # Very narrow range
    mask = calculate_thermal_habitat_mask(ds, temp_min=9.9, temp_max=10.1)

    # Should have some cells outside range
    assert float(mask.mean()) < 1.0  # Not everything matches
    assert float(mask.mean()) > 0.0  # Not everything is masked out


def test_thermal_habitat_mask_no_match():
    """Test mask when no data falls in range."""
    ds = create_test_dataset()

    # Data range is ~5-15, so this range shouldn't match
    mask = calculate_thermal_habitat_mask(ds, temp_min=20, temp_max=25)

    # All values should be 0
    assert float(mask.sum()) == 0


def test_thermal_habitat_mask_full_match():
    """Test mask when all data falls in range."""
    ds = create_test_dataset()

    mask = calculate_thermal_habitat_mask(ds, temp_min=0, temp_max=100)

    # All values should be 1
    assert float(mask.mean()) == 1.0
