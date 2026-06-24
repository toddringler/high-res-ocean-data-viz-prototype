from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import imageio.v2 as imageio
import numpy as np


REQUIRED_IMPORTS = [
    "xarray",
    "dask",
    "numpy",
    "pandas",
    "matplotlib",
    "cartopy",
    "netCDF4",
    "zarr",
    "yaml",
    "imageio",
    "imageio_ffmpeg",
]


def _check_imports() -> dict[str, bool]:
    result: dict[str, bool] = {}
    for module in REQUIRED_IMPORTS:
        try:
            __import__(module)
            result[module] = True
        except Exception:
            result[module] = False
    return result


def _check_cartopy_map() -> bool:
    try:
        import matplotlib.pyplot as plt
        import cartopy.crs as ccrs

        fig, ax = plt.subplots(subplot_kw={"projection": ccrs.PlateCarree()})
        ax.coastlines()
        plt.close(fig)
        return True
    except Exception:
        return False


def _check_xarray_open() -> bool:
    try:
        import xarray as xr

        ds = xr.Dataset({"sst": (("time", "lat", "lon"), np.zeros((1, 2, 2)))}, coords={"time": [0], "lat": [0, 1], "lon": [0, 1]})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.nc"
            ds.to_netcdf(path)
            xr.open_dataset(path)
        return True
    except Exception:
        return False


def _check_ffmpeg() -> bool:
    try:
        import imageio_ffmpeg

        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        completed = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True, check=False)
        return completed.returncode == 0
    except Exception:
        return False


def _check_mp4_write() -> bool:
    try:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "smoke.mp4"
            frames = [np.zeros((16, 16, 3), dtype=np.uint8), np.full((16, 16, 3), 255, dtype=np.uint8)]
            imageio.mimsave(target, frames, fps=2, codec="libx264")
            return target.exists() and target.stat().st_size > 0
    except Exception:
        return False


def check_dependencies() -> dict[str, object]:
    imports = _check_imports()
    report: dict[str, object] = {
        "python": sys.version_info >= (3, 10),
        "imports": imports,
        "cartopy_map": _check_cartopy_map(),
        "xarray_open": _check_xarray_open(),
        "ffmpeg": _check_ffmpeg(),
        "mp4_write": _check_mp4_write(),
    }
    report["ok"] = bool(report["python"] and all(imports.values()) and report["cartopy_map"] and report["xarray_open"] and report["ffmpeg"] and report["mp4_write"])
    return report
