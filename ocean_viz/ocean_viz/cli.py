from __future__ import annotations

import argparse
import json
import sys

from .animation import render_movie
from .diagnostics import check_dependencies
from .plotting import render_snapshot


def _cmd_check(_: argparse.Namespace) -> int:
    report = check_dependencies()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


def _cmd_snapshot(args: argparse.Namespace) -> int:
    print(render_snapshot(args.config))
    return 0


def _cmd_movie(args: argparse.Namespace) -> int:
    print(render_movie(args.config))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m ocean_viz.cli")
    sub = parser.add_subparsers(dest="command", required=True)

    check_parser = sub.add_parser("check", help="Run dependency smoke checks")
    check_parser.set_defaults(func=_cmd_check)

    snapshot_parser = sub.add_parser("snapshot", help="Render snapshot PNG")
    snapshot_parser.add_argument("config")
    snapshot_parser.set_defaults(func=_cmd_snapshot)

    movie_parser = sub.add_parser("movie", help="Render MP4 movie")
    movie_parser.add_argument("config")
    movie_parser.set_defaults(func=_cmd_movie)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
