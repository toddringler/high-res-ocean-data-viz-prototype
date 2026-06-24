"""Dependency checks and diagnostics."""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple


def check_python_version() -> Tuple[bool, str]:
    """Check Python version."""
    version = sys.version_info
    required = (3, 9)

    if version >= required:
        return True, f"✓ Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"✗ Python {version.major}.{version.minor} (requires >= 3.9)"


def check_imports() -> Tuple[bool, Dict[str, bool]]:
    """Check if required packages can be imported."""
    required_packages = [
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
    ]

    results = {}
    all_ok = True

    for pkg in required_packages:
        try:
            __import__(pkg)
            results[pkg] = True
        except ImportError as e:
            results[pkg] = False
            all_ok = False

    return all_ok, results


def check_ffmpeg() -> Tuple[bool, str]:
    """Check if ffmpeg is available."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            # Extract version line
            lines = result.stdout.split("\n")
            version_line = lines[0] if lines else "ffmpeg found"
            return True, f"✓ ffmpeg: {version_line[:50]}"
        else:
            return False, f"✗ ffmpeg exists but returned error"
    except FileNotFoundError:
        return False, f"✗ ffmpeg not found in PATH"
    except subprocess.TimeoutExpired:
        return False, f"✗ ffmpeg check timed out"
    except Exception as e:
        return False, f"✗ ffmpeg check failed: {e}"


def check_cartopy_map() -> Tuple[bool, str]:
    """Check if cartopy can create a simple map."""
    try:
        import matplotlib.pyplot as plt
        import cartopy.crs as ccrs

        fig = plt.figure(figsize=(4, 3))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()
        plt.close(fig)

        return True, "✓ Cartopy map creation works"
    except Exception as e:
        return False, f"✗ Cartopy map creation failed: {e}"


def check_xarray_netcdf() -> Tuple[bool, str]:
    """Check if xarray can handle NetCDF."""
    try:
        import xarray as xr
        import numpy as np
        import tempfile

        # Create synthetic dataset
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as f:
            temp_path = f.name

        try:
            ds = xr.Dataset(
                {
                    "temperature": (["time", "lat", "lon"], np.random.rand(10, 5, 5)),
                },
                coords={
                    "time": range(10),
                    "lat": range(5),
                    "lon": range(5),
                },
            )
            ds.to_netcdf(temp_path)
            ds_read = xr.open_dataset(temp_path)
            ds_read.close()

            return True, "✓ xarray NetCDF I/O works"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    except Exception as e:
        return False, f"✗ xarray NetCDF I/O failed: {e}"


def check_imageio_mp4() -> Tuple[bool, str]:
    """Check if imageio can write MP4."""
    try:
        import imageio
        import numpy as np
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            temp_path = f.name

        try:
            # Create writer and write 2 frames
            writer = imageio.get_writer(temp_path, fps=1)

            # Create simple test frames
            frame = np.zeros((100, 100, 3), dtype=np.uint8)
            frame[20:80, 20:80] = [255, 0, 0]

            writer.append_data(frame)
            writer.append_data(frame)
            writer.close()

            # Check if file was created
            if Path(temp_path).exists() and Path(temp_path).stat().st_size > 1000:
                return True, "✓ imageio MP4 writing works"
            else:
                return False, "✗ imageio MP4 file too small"

        finally:
            Path(temp_path).unlink(missing_ok=True)

    except Exception as e:
        return False, f"✗ imageio MP4 writing failed: {e}"


def run_full_check() -> Dict[str, Tuple[bool, str]]:
    """Run all dependency checks."""
    checks = {
        "python_version": check_python_version(),
        "ffmpeg": check_ffmpeg(),
        "cartopy_map": check_cartopy_map(),
        "xarray_netcdf": check_xarray_netcdf(),
        "imageio_mp4": check_imageio_mp4(),
    }

    # Check imports
    all_imports_ok, import_results = check_imports()

    if all_imports_ok:
        checks["imports"] = (True, "✓ All required packages import successfully")
    else:
        failed = [pkg for pkg, ok in import_results.items() if not ok]
        checks["imports"] = (False, f"✗ Import failed: {', '.join(failed)}")

    return checks


def print_checks():
    """Run and print all checks."""
    print("\n" + "=" * 60)
    print("Ocean Visualization - Dependency Check")
    print("=" * 60 + "\n")

    checks = run_full_check()

    for check_name, (ok, message) in checks.items():
        print(f"{check_name:.<40} {message}")

    all_ok = all(ok for ok, _ in checks.values())

    print("\n" + "=" * 60)
    if all_ok:
        print("✓ All checks passed! Ready to use ocean_viz.")
    else:
        print("✗ Some checks failed. Please install missing dependencies.")
    print("=" * 60 + "\n")

    return all_ok
