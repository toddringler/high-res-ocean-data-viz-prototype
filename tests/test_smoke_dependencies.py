"""Smoke tests for dependencies."""

import pytest
from ocean_viz.diagnostics import (
    check_python_version,
    check_imports,
    check_ffmpeg,
    check_cartopy_map,
    check_xarray_netcdf,
    check_imageio_mp4,
)


def test_check_python_version():
    """Test Python version check."""
    ok, msg = check_python_version()
    assert isinstance(ok, bool)
    assert isinstance(msg, str)
    assert "Python" in msg


def test_check_imports():
    """Test package import check."""
    ok, results = check_imports()
    assert isinstance(ok, bool)
    assert isinstance(results, dict)

    # Should have all required packages
    required = ["xarray", "numpy", "matplotlib", "cartopy"]
    for pkg in required:
        assert pkg in results
        assert isinstance(results[pkg], bool)


def test_check_ffmpeg():
    """Test ffmpeg check."""
    ok, msg = check_ffmpeg()
    assert isinstance(ok, bool)
    assert isinstance(msg, str)
    assert "ffmpeg" in msg.lower()


def test_check_cartopy_map():
    """Test cartopy map creation."""
    ok, msg = check_cartopy_map()
    assert isinstance(ok, bool)
    assert isinstance(msg, str)
    if ok:
        assert "Cartopy" in msg or "cartopy" in msg


def test_check_xarray_netcdf():
    """Test xarray NetCDF I/O."""
    ok, msg = check_xarray_netcdf()
    assert isinstance(ok, bool)
    assert isinstance(msg, str)
    if ok:
        assert "xarray" in msg or "NetCDF" in msg


def test_check_imageio_mp4():
    """Test imageio MP4 writing."""
    ok, msg = check_imageio_mp4()
    assert isinstance(ok, bool)
    assert isinstance(msg, str)
    if ok:
        assert "imageio" in msg or "MP4" in msg
