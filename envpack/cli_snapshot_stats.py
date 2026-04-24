"""CLI commands for snapshot statistics."""

from __future__ import annotations

import argparse
import glob
import json
import sys

from envpack.snapshot_stats import compute_stats, stats_from_directory


def cmd_stats(args: argparse.Namespace) -> None:
    """Print statistics for a directory or a list of snapshot files."""
    if args.directory:
        try:
            result = stats_from_directory(args.directory)
        except NotADirectoryError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        files: list[str] = []
        for pattern in args.files:
            matched = glob.glob(pattern)
            files.extend(matched if matched else [pattern])
        result = compute_stats(files)

    if result is None:
        print("No snapshots found.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        output = {
            "count": result.count,
            "total_keys": result.total_keys,
            "avg_keys": result.avg_keys,
            "min_keys": result.min_keys,
            "max_keys": result.max_keys,
            "common_keys": result.common_keys,
            "unique_keys": result.unique_keys,
            "key_frequency": result.key_frequency,
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.summary())
        if args.verbose:
            print("\nKey frequency:")
            for k, v in sorted(result.key_frequency.items(), key=lambda x: -x[1]):
                print(f"  {k}: {v}")


def register_stats_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("stats", help="Show statistics across multiple snapshots")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--directory", metavar="DIR", help="Directory of snapshot files")
    group.add_argument("files", nargs="*", metavar="FILE", default=None, help="Snapshot file paths")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    p.add_argument("-v", "--verbose", action="store_true", help="Show key frequency table")
    p.set_defaults(func=cmd_stats)
