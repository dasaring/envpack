"""CLI commands for snapshot locking."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envpack.snapshot_lock import (
    lock_snapshot,
    unlock_snapshot,
    is_locked,
    list_locks,
    _DEFAULT_LOCK_FILE,
)


def cmd_lock_add(args: argparse.Namespace) -> None:
    lock_file = Path(args.lock_file)
    added = lock_snapshot(args.snapshot, reason=args.reason or "", lock_file=lock_file)
    if added:
        print(f"Locked: {args.snapshot}")
    else:
        print(f"Already locked: {args.snapshot}")


def cmd_lock_remove(args: argparse.Namespace) -> None:
    lock_file = Path(args.lock_file)
    removed = unlock_snapshot(args.snapshot, lock_file=lock_file)
    if removed:
        print(f"Unlocked: {args.snapshot}")
    else:
        print(f"Not locked: {args.snapshot}", file=sys.stderr)
        sys.exit(1)


def cmd_lock_check(args: argparse.Namespace) -> None:
    lock_file = Path(args.lock_file)
    if is_locked(args.snapshot, lock_file=lock_file):
        print(f"LOCKED: {args.snapshot}")
    else:
        print(f"not locked: {args.snapshot}")
        sys.exit(1)


def cmd_lock_list(args: argparse.Namespace) -> None:
    lock_file = Path(args.lock_file)
    entries = list_locks(lock_file=lock_file)
    if not entries:
        print("No locked snapshots.")
        return
    for entry in entries:
        reason = f" — {entry['reason']}" if entry["reason"] else ""
        print(f"{entry['path']}{reason}")


def register_lock_commands(subparsers: argparse._SubParsersAction) -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--lock-file",
        default=str(_DEFAULT_LOCK_FILE),
        help="Path to lock store (default: .envpack_locks.json)",
    )

    p_add = subparsers.add_parser("lock-add", parents=[common], help="Lock a snapshot")
    p_add.add_argument("snapshot", help="Path to snapshot file")
    p_add.add_argument("--reason", default="", help="Optional reason for locking")
    p_add.set_defaults(func=cmd_lock_add)

    p_rm = subparsers.add_parser("lock-remove", parents=[common], help="Unlock a snapshot")
    p_rm.add_argument("snapshot", help="Path to snapshot file")
    p_rm.set_defaults(func=cmd_lock_remove)

    p_chk = subparsers.add_parser("lock-check", parents=[common], help="Check if a snapshot is locked")
    p_chk.add_argument("snapshot", help="Path to snapshot file")
    p_chk.set_defaults(func=cmd_lock_check)

    p_ls = subparsers.add_parser("lock-list", parents=[common], help="List all locked snapshots")
    p_ls.set_defaults(func=cmd_lock_list)
