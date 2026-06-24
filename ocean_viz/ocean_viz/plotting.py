from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from .config import load_config
from .dataset_loader import load_ocean_data


def _projection(name: str):
    try:
        import cartopy.crs as ccrs

        if name == "north_pacific_platecarree":
            return ccrs.PlateCarree(central_longitude=180), ccrs.PlateCarree()
        return ccrs.PlateCarree(), ccrs.PlateCarree()
    except Exception:  # pragma: no cover - optional fallback
        return None, None


def auto_filename(cfg: dict, output_type: str, date_or_range: str) -> str:
    return f"{cfg['dataset']['name']}_{cfg['variable']['name']}_{date_or_range}_{cfg['region']['name']}_{output_type}"


def _figure_size(cfg: dict) -> tuple[float, float]:
    dpi = cfg["output"].get("dpi", 200)
    resolution = cfg["output"].get("resolution", "1080p")
    mapping = {"1080p": (1920, 1080), "720p": (1280, 720), "4k": (3840, 2160)}
    width_px, height_px = mapping.get(str(resolution).lower(), mapping["1080p"])
    return width_px / dpi, height_px / dpi


def render_dataarray_map(da, cfg: dict, timestamp, out_path: str | Path, color_scale: dict):
    proj, data_transform = _projection(cfg["visual"].get("projection", "north_pacific_platecarree"))
    figsize = _figure_size(cfg)
    if proj is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig, ax = plt.subplots(figsize=figsize, subplot_kw={"projection": proj})
        import cartopy.feature as cfeature

        if cfg["visual"].get("show_land", True):
            ax.add_feature(cfeature.LAND, facecolor="0.85")
        if cfg["visual"].get("show_coastline", True):
            ax.coastlines(linewidth=0.7)
        region = cfg["region"]
        ax.set_extent([region["lon_min"], region["lon_max"], region["lat_min"], region["lat_max"]], crs=data_transform)

    kwargs = {
        "cmap": color_scale.get("cmap", "turbo"),
        "vmin": color_scale.get("vmin"),
        "vmax": color_scale.get("vmax"),
        "transform": data_transform,
    }
    if proj is None:
        kwargs.pop("transform")

    mesh = da.plot(ax=ax, add_colorbar=False, **kwargs)
    cbar = fig.colorbar(mesh, ax=ax, shrink=0.8)
    cbar.set_label(color_scale.get("units") or da.attrs.get("units", ""))

    title = f"{cfg['dataset']['name']} | {cfg['variable'].get('display_name', cfg['variable']['name'])} | {str(timestamp)[:10]}"
    ax.set_title(title)
    fig.savefig(out_path, dpi=cfg["output"].get("dpi", 200), bbox_inches="tight")
    plt.close(fig)


def render_snapshot(config_path: str | Path | dict) -> str:
    cfg = load_config(config_path)
    da = load_ocean_data(cfg)
    snapshot_cfg = cfg["output"].get("snapshot", {})
    target_date = snapshot_cfg.get("date")
    snap = da.sel(time=target_date) if target_date else da.isel(time=0)

    out_dir = Path(cfg["output"].get("output_dir", "outputs"))
    out_dir.mkdir(parents=True, exist_ok=True)

    date_token = str(snap["time"].values)[:10].replace("-", "")
    filename = auto_filename(cfg, "snapshot", date_token) + ".png"
    out_path = out_dir / filename

    color_scale = cfg["visual"].get("color_scale", {})
    render_dataarray_map(snap, cfg, snap["time"].values, out_path, color_scale)
    return str(out_path)
