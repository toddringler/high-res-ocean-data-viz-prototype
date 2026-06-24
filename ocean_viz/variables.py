"""Ocean variable definitions and metadata."""

from typing import Dict, Any, Optional

# Variable catalog with metadata
VARIABLES_CATALOG = {
    "sst": {
        "display_name": "Sea surface temperature",
        "units": "degC",
        "long_name": "sea surface temperature",
        "standard_names": ["sea_surface_temperature", "thetao"],
        "vmin": 4,
        "vmax": 16,
        "cmap": "turbo",
        "is_3d": True,
    },
    "u_current": {
        "display_name": "Eastward current",
        "units": "m/s",
        "long_name": "eastward ocean current",
        "standard_names": ["eastward_sea_water_velocity", "uo"],
        "vmin": -1,
        "vmax": 1,
        "cmap": "RdBu_r",
        "is_3d": True,
    },
    "v_current": {
        "display_name": "Northward current",
        "units": "m/s",
        "long_name": "northward ocean current",
        "standard_names": ["northward_sea_water_velocity", "vo"],
        "vmin": -1,
        "vmax": 1,
        "cmap": "RdBu_r",
        "is_3d": True,
    },
    "current_speed": {
        "display_name": "Current speed",
        "units": "m/s",
        "long_name": "ocean current speed",
        "vmin": 0,
        "vmax": 1,
        "cmap": "plasma",
        "is_3d": False,
        "is_derived": True,
    },
    "salinity": {
        "display_name": "Sea water salinity",
        "units": "psu",
        "long_name": "sea water salinity",
        "standard_names": ["sea_water_salinity", "so"],
        "vmin": 30,
        "vmax": 34,
        "cmap": "viridis",
        "is_3d": True,
    },
    "mld": {
        "display_name": "Mixed layer depth",
        "units": "m",
        "long_name": "ocean mixed layer thickness",
        "standard_names": ["ocean_mixed_layer_thickness"],
        "vmin": 0,
        "vmax": 100,
        "cmap": "viridis",
        "is_3d": False,
    },
    "ssh": {
        "display_name": "Sea surface height",
        "units": "m",
        "long_name": "sea surface height above geoid",
        "standard_names": ["sea_surface_height_above_geoid", "zos"],
        "vmin": -1,
        "vmax": 1,
        "cmap": "balance",
        "is_3d": False,
    },
    "chlorophyll": {
        "display_name": "Chlorophyll concentration",
        "units": "mg/m^3",
        "long_name": "mass concentration of chlorophyll",
        "standard_names": ["mass_concentration_of_chlorophyll"],
        "vmin": 0,
        "vmax": 5,
        "cmap": "viridis",
        "is_3d": False,
    },
    "sst_gradient_strength": {
        "display_name": "SST gradient strength",
        "units": "degC/km",
        "long_name": "magnitude of horizontal SST gradient",
        "vmin": 0,
        "vmax": 2,
        "cmap": "hot",
        "is_3d": False,
        "is_derived": True,
    },
    "sst_anomaly": {
        "display_name": "SST anomaly",
        "units": "degC",
        "long_name": "sea surface temperature anomaly",
        "vmin": -3,
        "vmax": 3,
        "cmap": "RdBu_r",
        "is_3d": False,
        "is_derived": True,
    },
    "thermal_habitat_mask": {
        "display_name": "Thermal habitat mask",
        "units": "boolean",
        "long_name": "thermal habitat suitability mask",
        "vmin": 0,
        "vmax": 1,
        "cmap": "RdYlGn",
        "is_3d": False,
        "is_derived": True,
    },
}


def get_variable_metadata(var_name: str) -> Dict[str, Any]:
    """Get metadata for a variable."""
    if var_name not in VARIABLES_CATALOG:
        available = ", ".join(VARIABLES_CATALOG.keys())
        raise ValueError(
            f"Variable '{var_name}' not found in catalog. Available: {available}"
        )
    return VARIABLES_CATALOG[var_name].copy()


def get_available_variables() -> list:
    """Get list of available variables."""
    return list(VARIABLES_CATALOG.keys())


def is_derived_variable(var_name: str) -> bool:
    """Check if variable is derived."""
    meta = get_variable_metadata(var_name)
    return meta.get("is_derived", False)


def is_3d_variable(var_name: str) -> bool:
    """Check if variable is 3D (has depth dimension)."""
    meta = get_variable_metadata(var_name)
    return meta.get("is_3d", False)


def get_default_color_scale(var_name: str) -> Dict[str, Any]:
    """Get default color scale for variable."""
    meta = get_variable_metadata(var_name)
    return {
        "vmin": meta.get("vmin", 0),
        "vmax": meta.get("vmax", 1),
        "cmap": meta.get("cmap", "viridis"),
    }
