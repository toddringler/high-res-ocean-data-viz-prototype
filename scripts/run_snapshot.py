"""Example script: Render a single snapshot."""

import sys
from pathlib import Path

# Add package to path if running from scripts directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from ocean_viz import render_snapshot

if __name__ == "__main__":
    config_path = Path(__file__).parent.parent / "configs" / "glorys12_sst_demo.yaml"

    print(f"Rendering snapshot using config: {config_path}")

    try:
        output_path = render_snapshot(str(config_path))
        print(f"✓ Snapshot saved to: {output_path}")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
