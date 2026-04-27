"""CLI commands for snapshot scoring."""
from __future__ import annotations

import argparse
import sys

from envpack.snapshot_score import score_snapshot


def cmd_score(args: argparse.Namespace) -> None:
    required = args.require.split(",") if getattr(args, "require", None) else None
    try:
        result = score_snapshot(args.snapshot, required_keys=required)
    except FileNotFoundError:
        print(f"error: snapshot not found: {args.snapshot}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(result.summary())

    if getattr(args, "min_score", None) is not None:
        if result.percent < args.min_score:
            print(
                f"FAIL: score {result.percent}% is below threshold {args.min_score}%",
                file=sys.stderr,
            )
            sys.exit(1)


def register_score_commands(
    subparsers: argparse._SubParsersAction,
) -> None:
    p = subparsers.add_parser("score", help="Score snapshot quality")
    p.add_argument("snapshot", help="Path to snapshot file")
    p.add_argument(
        "--require",
        metavar="KEYS",
        default=None,
        help="Comma-separated list of required keys",
    )
    p.add_argument(
        "--min-score",
        type=float,
        metavar="PCT",
        default=None,
        dest="min_score",
        help="Exit 1 if score percent is below this threshold",
    )
    p.set_defaults(func=cmd_score)
