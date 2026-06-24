# high-res-ocean-data-viz-prototype

Notebook-first Python prototype for loading and visualizing GLORYS12V1 ocean reanalysis surface fields.

## Quick start

```bash
cd ocean_viz
python -m ocean_viz.cli check
python -m ocean_viz.cli snapshot configs/glorys12_sst_demo.yaml
python -m ocean_viz.cli movie configs/glorys12_sst_demo.yaml
```

## Public API

```python
from ocean_viz import load_ocean_data, render_snapshot, render_movie

field = load_ocean_data("configs/glorys12_sst_demo.yaml")
png_path = render_snapshot("configs/glorys12_sst_demo.yaml")
mp4_path = render_movie("configs/glorys12_sst_demo.yaml")
```
