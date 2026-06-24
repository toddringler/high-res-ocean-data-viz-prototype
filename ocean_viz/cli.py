"""Command-line interface for ocean visualization."""

import argparse
import sys
from pathlib import Path

from ocean_viz.diagnostics import print_checks
from ocean_viz.plotting import render_snapshot
from ocean_viz.animation import render_movie


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ocean visualization CLI for GLORYS12V1 data"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Check command
    subparsers.add_parser("check", help="Run dependency checks")

    # Snapshot command
    snapshot_parser = subparsers.add_parser("snapshot", help="Render PNG snapshot")
    snapshot_parser.add_argument("config", help="Path to config file")
    snapshot_parser.add_argument("--date", help="Date to render (ISO format)")

    # Movie command
    movie_parser = subparsers.add_parser("movie", help="Render MP4 movie")
    movie_parser.add_argument("config", help="Path to config file")
    movie_parser.add_argument("--fps", type=int, help="Frames per second")

    args = parser.parse_args()

    if args.command == "check":
        success = print_checks()
        sys.exit(0 if success else 1)

    elif args.command == "snapshot":
        try:
            output_path = render_snapshot(args.config, date=args.date)
            print(f"✓ Snapshot saved to: {output_path}")
            sys.exit(0)
        except Exception as e:
            print(f"✗ Snapshot rendering failed: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "movie":
        try:
            kwargs = {"config_path": args.config}
            if args.fps is not None:
                kwargs["fps"] = args.fps
            output_path = render_movie(**kwargs)
            print(f"✓ Movie saved to: {output_path}")
            sys.exit(0)
        except Exception as e:
            print(f"✗ Movie rendering failed: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
