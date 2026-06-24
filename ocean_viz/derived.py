"""Derived variable calculations."""

import xarray as xr
import numpy as np
from typing import Dict, Any

from ocean_viz.dataset_loader import extract_surface_layer


def calculate_current_speed(
    ds: xr.Dataset, u_var: str = "uo", v_var: str = "vo"
) -> xr.DataArray:
    """Calculate current speed from u and v components.
    
    current_speed = sqrt(u^2 + v^2)
    """
    if u_var not in ds.data_vars or v_var not in ds.data_vars:
        available = ", ".join(ds.data_vars)
        raise ValueError(
            f"Required variables '{u_var}' and/or '{v_var}' not found. "
            f"Available: {available}"
        )

    u = ds[u_var]
    v = ds[v_var]

    speed = np.sqrt(u**2 + v**2)
    speed.name = "current_speed"

    return speed


def calculate_sst_gradient(ds: xr.Dataset, sst_var: str = "thetao") -> xr.DataArray:
    """Calculate SST gradient strength.
    
    gradient = sqrt((d_sst/dx)^2 + (d_sst/dy)^2)
    """
    if sst_var not in ds.data_vars:
        available = ", ".join(ds.data_vars)
        raise ValueError(
            f"Variable '{sst_var}' not found. Available: {available}"
        )

    sst = ds[sst_var]

    # Compute gradients along lon and lat
    # Use edge handling to maintain dimensions
    grad_lon = np.abs(sst.differentiate("lon", edge_dim="trim")) if "lon" in sst.dims else sst * 0
    grad_lat = np.abs(sst.differentiate("lat", edge_dim="trim")) if "lat" in sst.dims else sst * 0

    # Combine gradients
    gradient = np.sqrt(grad_lon**2 + grad_lat**2)
    gradient.name = "sst_gradient_strength"

    return gradient


def calculate_sst_anomaly(
    ds: xr.Dataset, sst_var: str = "thetao", climatology_ds: xr.Dataset = None
) -> xr.DataArray:
    """Calculate SST anomaly.
    
    anomaly = sst - climatology (or temporal mean if no climatology provided)
    """
    if sst_var not in ds.data_vars:
        available = ", ".join(ds.data_vars)
        raise ValueError(
            f"Variable '{sst_var}' not found. Available: {available}"
        )

    sst = ds[sst_var]

    if climatology_ds is not None:
        if sst_var in climatology_ds.data_vars:
            climatology = climatology_ds[sst_var]
        else:
            raise ValueError(f"Climatology variable '{sst_var}' not found")
    else:
        # Use temporal mean as baseline
        climatology = sst.mean(dim="time")

    anomaly = sst - climatology
    anomaly.name = "sst_anomaly"

    return anomaly


def calculate_thermal_habitat_mask(
    ds: xr.Dataset,
    sst_var: str = "thetao",
    temp_min: float = 5.0,
    temp_max: float = 15.0,
) -> xr.DataArray:
    """Calculate thermal habitat mask.
    
    mask = True where temp_min <= sst <= temp_max
    """
    if sst_var not in ds.data_vars:
        available = ", ".join(ds.data_vars)
        raise ValueError(
            f"Variable '{sst_var}' not found. Available: {available}"
        )

    sst = ds[sst_var]

    mask = (sst >= temp_min) & (sst <= temp_max)
    mask.name = "thermal_habitat_mask"

    return mask.astype(float)


def apply_derived_variables(
    ds: xr.Dataset, derived_config: Dict[str, Any]
) -> xr.Dataset:
    """Apply derived variable calculations based on configuration.
    
    derived_config should contain:
    - enabled: bool
    - variables: dict of derived variable configs
    """
    if not derived_config.get("enabled", False):
        return ds

    result_vars = {}

    variables = derived_config.get("variables", {})

    for var_name, var_config in variables.items():
        var_type = var_config.get("type")

        if var_type == "current_speed":
            u_var = var_config.get("u_var", "uo")
            v_var = var_config.get("v_var", "vo")
            result_vars[var_name] = calculate_current_speed(ds, u_var, v_var)

        elif var_type == "sst_gradient":
            sst_var = var_config.get("sst_var", "thetao")
            result_vars[var_name] = calculate_sst_gradient(ds, sst_var)

        elif var_type == "sst_anomaly":
            sst_var = var_config.get("sst_var", "thetao")
            result_vars[var_name] = calculate_sst_anomaly(ds, sst_var)

        elif var_type == "thermal_habitat_mask":
            sst_var = var_config.get("sst_var", "thetao")
            temp_min = var_config.get("temp_min", 5.0)
            temp_max = var_config.get("temp_max", 15.0)
            result_vars[var_name] = calculate_thermal_habitat_mask(
                ds, sst_var, temp_min, temp_max
            )

    # Add derived variables to dataset
    for var_name, data in result_vars.items():
        ds[var_name] = data

    return ds
