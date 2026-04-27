"""CLI commands for snapshot deduplication."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envpack.snapshot_dedup import (
    dedup_summary,
    find_duplicates_in_dir,
)


def cmd_dedup_find(args: argparse.Namespace) -> None:
    """List duplicate snapshots found in a directory."""
    directory = Path(args.directory)
    try:
        groups = find_duplicates_in_dir(directory)
    except NotADirectoryError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(dedup_summary(groups))


def cmd_dedup_remove(args: argparse.Namespace) -> None:
    """Remove duplicate snapshot files, keeping the canonical copy."""
    directory = Path(args.directory)
    try:
        groups = find_duplicates_in_dir(directory)
    except NotADirectoryError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not groups:
        print("No duplicates found.")
        return

    removed = 0
    for group in groups:
        for dup in group.duplicates():
            if args.dry_run:
                print(f"[dry-run] would remove: {dup}")
            else:
                dup.unlink()
                print(f"Removed: {dup}")
            removed += 1

    if args.dry_run:
        print(f"[dry-run] {removed} file(s) would be removed.")
    else:
        print(f"{removed} duplicate file(s) removed.")


def register_dedup_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    find_p = subparsers.add_parser("dedup-find", help="Find duplicate snapshots")
    find_p.add_argument("directory", help="Directory to scan")
    find_p.set_defaults(func=cmd_dedup_find)

    remove_p = subparsers.add_parser("dedup-remove", help="Remove duplicate snapshots")
    remove_p.add_argument("directory", help="Directory to scan")
    remove_p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show what would be removed without deleting",
    )
    remove_p.set_defaults(func=cmd_dedup_remove)
