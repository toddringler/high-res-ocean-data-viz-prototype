"""Dataset-specific adapters for different data sources."""

from typing import Dict, Any, Optional, List
import xarray as xr


class DatasetAdapter:
    """Base class for dataset adapters."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize adapter with dataset config."""
        self.config = config
        self.access = config.get("access", {})
        self.name = config.get("name", "unknown")

    def open_dataset(
        self, lon_range: tuple, lat_range: tuple, time_range: tuple
    ) -> xr.Dataset:
        """Open dataset with spatial and temporal subsetting."""
        raise NotImplementedError

    def get_available_variables(self) -> List[str]:
        """Get list of variables available in dataset."""
        raise NotImplementedError

    def normalize_coordinates(self, ds: xr.Dataset) -> xr.Dataset:
        """Normalize dimension and coordinate names."""
        return ds


class GLORYS12Adapter(DatasetAdapter):
    """Adapter for GLORYS12V1 data."""

    def open_dataset(
        self, lon_range: tuple, lat_range: tuple, time_range: tuple
    ) -> xr.Dataset:
        """Open GLORYS12V1 files with subsetting."""
        file_pattern = self.access.get("path", "*.nc")
        engine = self.access.get("engine", "netcdf4")

        # Open multiple files with xarray
        ds = xr.open_mfdataset(file_pattern, engine=engine, combine="by_coords")

        # Normalize coordinates
        ds = self.normalize_coordinates(ds)

        # Subset by time
        time_start, time_end = time_range
        ds = ds.sel(time=slice(time_start, time_end))

        # Subset by region (handle dateline)
        lon_min, lon_max = lon_range
        lat_min, lat_max = lat_range

        # Handle longitude subsetting with dateline-crossing
        if lon_min < lon_max:
            # Normal case: lon_min < lon_max
            ds = ds.sel(lon=slice(lon_min, lon_max), lat=slice(lat_min, lat_max))
        else:
            # Dateline-crossing case: lon_min > lon_max
            # Select lon_min to 360 OR 0 to lon_max
            ds1 = ds.sel(lon=slice(lon_min, 360), lat=slice(lat_min, lat_max))
            ds2 = ds.sel(lon=slice(0, lon_max), lat=slice(lat_min, lat_max))
            ds = xr.concat([ds1, ds2], dim="lon")

        return ds

    def normalize_coordinates(self, ds: xr.Dataset) -> xr.Dataset:
        """Normalize GLORYS12V1 coordinate names."""
        # Common GLORYS dimension names
        dim_mappings = {"x": "lon", "y": "lat", "depth": "depth", "time": "time"}

        for old_name, new_name in dim_mappings.items():
            if old_name in ds.dims and new_name not in ds.dims:
                ds = ds.rename({old_name: new_name})

        # Ensure coordinates are present
        for coord_name in ["lon", "lat", "time"]:
            if coord_name not in ds.coords and coord_name in ds.dims:
                ds.coords[coord_name] = ds[coord_name]

        return ds

    def get_available_variables(self) -> List[str]:
        """Get available variables in GLORYS12V1."""
        # Common GLORYS12V1 variables
        return [
            "thetao",  # sea water potential temperature
            "so",  # sea water salinity
            "uo",  # eastward ocean current
            "vo",  # northward ocean current
            "zos",  # sea surface height
            "mlotst",  # ocean mixed layer thickness
        ]


class LocalNetCDFAdapter(DatasetAdapter):
    """Generic adapter for local NetCDF files."""

    def open_dataset(
        self, lon_range: tuple, lat_range: tuple, time_range: tuple
    ) -> xr.Dataset:
        """Open local NetCDF files."""
        file_pattern = self.access.get("path", "*.nc")
        engine = self.access.get("engine", "netcdf4")

        ds = xr.open_mfdataset(file_pattern, engine=engine, combine="by_coords")
        ds = self.normalize_coordinates(ds)

        # Subset by time
        time_start, time_end = time_range
        if "time" in ds.dims:
            ds = ds.sel(time=slice(time_start, time_end))

        # Subset by region
        lon_min, lon_max = lon_range
        lat_min, lat_max = lat_range

        if "lon" in ds.dims:
            if lon_min < lon_max:
                ds = ds.sel(lon=slice(lon_min, lon_max))
            else:
                ds1 = ds.sel(lon=slice(lon_min, 360))
                ds2 = ds.sel(lon=slice(0, lon_max))
                ds = xr.concat([ds1, ds2], dim="lon")

        if "lat" in ds.dims:
            ds = ds.sel(lat=slice(lat_min, lat_max))

        return ds

    def get_available_variables(self) -> List[str]:
        """Get available variables in local files."""
        file_pattern = self.access.get("path", "*.nc")
        engine = self.access.get("engine", "netcdf4")

        ds = xr.open_mfdataset(file_pattern, engine=engine, combine="by_coords")
        return list(ds.data_vars)


class ZarrAdapter(DatasetAdapter):
    """Adapter for Zarr stores."""

    def open_dataset(
        self, lon_range: tuple, lat_range: tuple, time_range: tuple
    ) -> xr.Dataset:
        """Open Zarr store."""
        store_path = self.access.get("path", ".")

        ds = xr.open_zarr(store_path)
        ds = self.normalize_coordinates(ds)

        # Subset by time
        time_start, time_end = time_range
        if "time" in ds.dims:
            ds = ds.sel(time=slice(time_start, time_end))

        # Subset by region
        lon_min, lon_max = lon_range
        lat_min, lat_max = lat_range

        if "lon" in ds.dims:
            if lon_min < lon_max:
                ds = ds.sel(lon=slice(lon_min, lon_max))
            else:
                ds1 = ds.sel(lon=slice(lon_min, 360))
                ds2 = ds.sel(lon=slice(0, lon_max))
                ds = xr.concat([ds1, ds2], dim="lon")

        if "lat" in ds.dims:
            ds = ds.sel(lat=slice(lat_min, lat_max))

        return ds

    def get_available_variables(self) -> List[str]:
        """Get available variables in Zarr store."""
        store_path = self.access.get("path", ".")
        ds = xr.open_zarr(store_path)
        return list(ds.data_vars)


def get_adapter(dataset_config: Dict[str, Any]) -> DatasetAdapter:
    """Factory function to get appropriate adapter."""
    adapter_name = dataset_config.get("adapter", "local_netcdf").lower()

    adapters = {
        "glorys12": GLORYS12Adapter,
        "local_netcdf": LocalNetCDFAdapter,
        "local_zarr": ZarrAdapter,
        "zarr": ZarrAdapter,
    }

    adapter_class = adapters.get(adapter_name)
    if adapter_class is None:
        raise ValueError(
            f"Unknown adapter: {adapter_name}. Available: {', '.join(adapters.keys())}"
        )

    return adapter_class(dataset_config)
