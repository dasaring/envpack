"""CLI commands for snapshot masking."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envpack.snapshot_mask import DEFAULT_MASK, MaskError, mask_file


def cmd_mask(args: argparse.Namespace) -> None:
    """Mask keys in a snapshot file by name or regex pattern."""
    if not args.keys and not args.pattern:
        print("error: provide --keys and/or --pattern", file=sys.stderr)
        sys.exit(1)

    keys = args.keys or None
    try:
        dest = mask_file(
            path=args.snapshot,
            keys=keys,
            pattern=args.pattern,
            mask=args.mask,
            output=args.output,
        )
    except MaskError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(str(dest))


def register_mask_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("mask", help="Mask sensitive keys in a snapshot")
    p.add_argument("snapshot", type=Path, help="Path to snapshot JSON file")
    p.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        default=[],
        help="Exact key names to mask",
    )
    p.add_argument(
        "--pattern",
        metavar="REGEX",
        default=None,
        help="Regex pattern; matching keys are masked",
    )
    p.add_argument(
        "--mask",
        default=DEFAULT_MASK,
        help=f"Replacement value (default: {DEFAULT_MASK!r})",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write masked snapshot to this path (default: overwrite source)",
    )
    p.set_defaults(func=cmd_mask)
