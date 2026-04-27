"""CLI commands for sorting snapshot keys."""
from __future__ import annotations

import argparse
import sys

from envpack.snapshot_sort import SortError, sort_file


def cmd_sort(args: argparse.Namespace) -> None:
    """Sort keys in a snapshot file."""
    try:
        keys = args.keys.split(",") if getattr(args, "keys", None) else None
        result = sort_file(args.path, strategy=args.strategy, keys=keys)
        print(f"Sorted: {result}")
    except FileNotFoundError:
        print(f"Error: snapshot not found: {args.path}", file=sys.stderr)
        sys.exit(1)
    except SortError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_sort_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``sort`` sub-command."""
    p = subparsers.add_parser(
        "sort",
        help="Sort the keys of a snapshot file",
    )
    p.add_argument("path", help="Path to the snapshot JSON file")
    p.add_argument(
        "--strategy",
        default="alpha",
        choices=["alpha", "alpha_desc", "length", "length_desc", "natural"],
        help="Sort strategy (default: alpha)",
    )
    p.add_argument(
        "--keys",
        default=None,
        metavar="KEY1,KEY2,...",
        help="Comma-separated list of keys to sort (others appended at end)",
    )
    p.set_defaults(func=cmd_sort)
