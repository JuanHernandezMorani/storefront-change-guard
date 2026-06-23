"""Minimal CLI scaffold for the prototype bootstrap phase."""

from __future__ import annotations

import argparse
from pathlib import Path

from agent_solution import __version__
from agent_solution.core.paths import project_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="storefront-guard",
        description="Local-first, evidence-based storefront change review prototype.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command")
    status_parser = subparsers.add_parser(
        "status",
        help="Show the current bootstrap status and resolved project root.",
    )
    status_parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Optional explicit project root. Defaults to automatic discovery.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "status":
        root = args.project_root.resolve() if args.project_root else project_root()
        print("Storefront Change Guard bootstrap scaffold")
        print(f"Version: {__version__}")
        print(f"Project root: {root}")
        print("Implemented capabilities: package bootstrap only")
        print("Next milestone: Phase 00 repository baseline audit")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
