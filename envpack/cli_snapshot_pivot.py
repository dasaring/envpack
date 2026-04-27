"""CLI commands for snapshot-pivot feature."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envpack.snapshot_pivot import PivotError, build_pivot, divergent_keys, pivot_to_rows


def cmd_pivot(args: argparse.Namespace) -> None:
    paths = [Path(p) for p in args.snapshots]
    try:
        pivot = build_pivot(paths)
    except PivotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.divergent_only:
        keys = divergent_keys(pivot)
        pivot = {k: pivot[k] for k in keys}

    if args.format == "json":
        print(json.dumps(pivot_to_rows(pivot), indent=2))
    else:
        # human-readable table
        labels = list(next(iter(pivot.values())).keys()) if pivot else []
        col_w = max((len(k) for k in pivot), default=3)
        val_w = 30

        header = f"{'KEY':<{col_w}}  " + "  ".join(f"{l:<{val_w}}" for l in labels)
        print(header)
        print("-" * len(header))
        for key, values in pivot.items():
            row = f"{key:<{col_w}}  " + "  ".join(
                f"{str(v) if v is not None else '(missing)'):<{val_w}}" for v in values.values()
            )
            print(row)


def register_pivot_commands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "pivot",
        help="Transpose multiple snapshots into a key-centric comparison table.",
    )
    p.add_argument("snapshots", nargs="+", metavar="SNAPSHOT",
                   help="Two or more snapshot files to compare.")
    p.add_argument("--divergent-only", action="store_true",
                   help="Show only keys that differ across snapshots.")
    p.add_argument("--format", choices=["table", "json"], default="table",
                   help="Output format (default: table).")
    p.set_defaults(func=cmd_pivot)
