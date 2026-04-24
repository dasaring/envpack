"""CLI commands for snapshot search."""

from __future__ import annotations

import argparse
import sys

from envpack.snapshot_search import search_snapshots


def cmd_search(args: argparse.Namespace) -> None:
    if not args.key and not args.value:
        print("error: provide --key and/or --value", file=sys.stderr)
        sys.exit(1)

    try:
        results = search_snapshots(
            directory=args.directory,
            key_pattern=args.key or None,
            value_pattern=args.value or None,
        )
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print("No matching snapshots found.")
        return

    for result in results:
        print(result.path)
        for k in result.matched_keys:
            print(f"  {k}")


def register_search_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("search", help="Search snapshots by key or value pattern")
    p.add_argument("directory", help="Directory containing snapshot JSON files")
    p.add_argument("--key", default="", help="Glob pattern to match against key names")
    p.add_argument("--value", default="", help="Glob pattern to match against values")
    p.set_defaults(func=cmd_search)
