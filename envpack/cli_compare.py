"""CLI subcommands for snapshot comparison."""

from __future__ import annotations

import argparse
import sys

from envpack.compare import compare_files, compare_to_current, report
from envpack.diff import is_empty


def cmd_compare(args: argparse.Namespace) -> None:
    """Compare two snapshot files or a snapshot against the current env."""
    if args.current:
        keys = args.keys.split(",") if args.keys else None
        result = compare_to_current(args.snapshot_a, keys=keys)
        label = f"{args.snapshot_a} vs current environment"
    else:
        if not args.snapshot_b:
            print("error: provide --current or a second snapshot file.", file=sys.stderr)
            sys.exit(1)
        result = compare_files(args.snapshot_a, args.snapshot_b)
        label = f"{args.snapshot_a} vs {args.snapshot_b}"

    print(f"Comparing: {label}")
    print(report(result, verbose=args.verbose))

    if not is_empty(result):
        sys.exit(1)


def register_compare_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "compare",
        help="Compare two snapshots or a snapshot against the live environment.",
    )
    p.add_argument("snapshot_a", help="First (base) snapshot file.")
    p.add_argument("snapshot_b", nargs="?", default=None, help="Second snapshot file.")
    p.add_argument(
        "--current",
        action="store_true",
        help="Compare snapshot_a against the current environment instead.",
    )
    p.add_argument(
        "--keys",
        default=None,
        help="Comma-separated list of keys to compare (only with --current).",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Show actual values in the report.",
    )
    p.set_defaults(func=cmd_compare)
