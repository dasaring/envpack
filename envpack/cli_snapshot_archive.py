"""CLI commands for snapshot archiving."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envpack.snapshot_archive import (
    ArchiveError,
    archive_snapshot,
    is_archived,
    list_archived,
    unarchive_snapshot,
)

_DEFAULT_ARCHIVE_DIR = Path(".envpack_archive")


def cmd_archive(args: argparse.Namespace) -> None:
    archive_dir = Path(args.archive_dir)
    try:
        dest = archive_snapshot(Path(args.snapshot), archive_dir)
        print(f"Archived: {dest}")
    except ArchiveError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_unarchive(args: argparse.Namespace) -> None:
    archive_dir = Path(args.archive_dir)
    dest_dir = Path(args.dest_dir)
    try:
        dest = unarchive_snapshot(args.name, dest_dir, archive_dir, overwrite=args.overwrite)
        print(f"Restored: {dest}")
    except ArchiveError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_archive_list(args: argparse.Namespace) -> None:
    archive_dir = Path(args.archive_dir)
    names = list_archived(archive_dir)
    if not names:
        print("No archived snapshots.")
    else:
        for name in names:
            print(name)


def cmd_archive_check(args: argparse.Namespace) -> None:
    archive_dir = Path(args.archive_dir)
    if is_archived(args.name, archive_dir):
        print(f"'{args.name}' is archived.")
    else:
        print(f"'{args.name}' is NOT archived.")
        sys.exit(1)


def register_archive_commands(subparsers: argparse._SubParsersAction) -> None:
    ad = str(_DEFAULT_ARCHIVE_DIR)

    p_arch = subparsers.add_parser("archive", help="Move a snapshot to the archive")
    p_arch.add_argument("snapshot", help="Path to the snapshot file")
    p_arch.add_argument("--archive-dir", default=ad)
    p_arch.set_defaults(func=cmd_archive)

    p_un = subparsers.add_parser("unarchive", help="Restore a snapshot from the archive")
    p_un.add_argument("name", help="Filename of the archived snapshot")
    p_un.add_argument("dest_dir", help="Directory to restore the snapshot into")
    p_un.add_argument("--archive-dir", default=ad)
    p_un.add_argument("--overwrite", action="store_true")
    p_un.set_defaults(func=cmd_unarchive)

    p_ls = subparsers.add_parser("archive-list", help="List archived snapshots")
    p_ls.add_argument("--archive-dir", default=ad)
    p_ls.set_defaults(func=cmd_archive_list)

    p_chk = subparsers.add_parser("archive-check", help="Check if a snapshot is archived")
    p_chk.add_argument("name")
    p_chk.add_argument("--archive-dir", default=ad)
    p_chk.set_defaults(func=cmd_archive_check)
