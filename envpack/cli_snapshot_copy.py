"""CLI sub-commands for snapshot copy/clone operations."""
from __future__ import annotations

import argparse
import sys

from envpack.snapshot_copy import CopyError, clone_snapshot, copy_snapshot


def cmd_copy(args: argparse.Namespace) -> None:
    include = args.include.split(",") if args.include else None
    exclude = args.exclude.split(",") if args.exclude else None

    try:
        dest = copy_snapshot(
            args.src,
            args.dest,
            include_keys=include,
            exclude_keys=exclude,
            overwrite=args.overwrite,
        )
    except CopyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"copied: {dest}")
    if include:
        print(f"  included keys : {', '.join(sorted(include))}")
    if exclude:
        print(f"  excluded keys : {', '.join(sorted(exclude))}")


def cmd_clone(args: argparse.Namespace) -> None:
    try:
        dest = clone_snapshot(args.src, args.dest, overwrite=args.overwrite)
    except CopyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"cloned: {dest}")


def register_copy_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # --- copy ---
    p_copy = subparsers.add_parser("copy", help="copy a snapshot, optionally filtering keys")
    p_copy.add_argument("src", help="source snapshot file")
    p_copy.add_argument("dest", help="destination snapshot file")
    p_copy.add_argument("--include", metavar="KEYS", help="comma-separated keys to keep")
    p_copy.add_argument("--exclude", metavar="KEYS", help="comma-separated keys to drop")
    p_copy.add_argument("--overwrite", action="store_true", help="overwrite destination if it exists")
    p_copy.set_defaults(func=cmd_copy)

    # --- clone ---
    p_clone = subparsers.add_parser("clone", help="clone a snapshot (full copy)")
    p_clone.add_argument("src", help="source snapshot file")
    p_clone.add_argument("dest", help="destination snapshot file")
    p_clone.add_argument("--overwrite", action="store_true", help="overwrite destination if it exists")
    p_clone.set_defaults(func=cmd_clone)
