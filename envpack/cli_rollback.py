"""CLI commands for rollback functionality."""

from __future__ import annotations

import argparse
from pathlib import Path

from envpack.rollback import get_rollback_target, rollback, RollbackError
from envpack.diff import summary as diff_summary, is_empty

DEFAULT_HISTORY = Path(".envpack_history.json")


def cmd_rollback(args: argparse.Namespace) -> None:
    """Execute the rollback command.

    Resolves the target snapshot from history (by label or index), computes
    the diff against the destination, and optionally writes the rollback.
    """
    history_file = Path(getattr(args, "history_file", DEFAULT_HISTORY))
    label = getattr(args, "label", None)
    index = getattr(args, "index", -1)
    dest = args.dest
    dry_run = getattr(args, "dry_run", False)

    try:
        entry = get_rollback_target(history_file, label=label, index=index)
    except RollbackError as exc:
        print(f"[rollback] error: {exc}")
        raise SystemExit(1)

    source_path = entry["path"]
    print(f"[rollback] target snapshot: {source_path}")
    if entry.get("label"):
        print(f"[rollback] label: {entry['label']}")

    try:
        result = rollback(source_path, dest, dry_run=dry_run)
    except FileNotFoundError as exc:
        print(f"[rollback] error: snapshot file not found — {exc}")
        raise SystemExit(1)
    except Exception as exc:
        print(f"[rollback] error: {exc}")
        raise SystemExit(1)

    diff = result["diff"]
    if is_empty(diff):
        print("[rollback] no changes (snapshot is identical to current)")
    else:
        print("[rollback] changes:")
        print(diff_summary(diff))

    if dry_run:
        print("[rollback] dry-run mode — no files written")
    else:
        print(f"[rollback] written to {dest}")


def register_rollback_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'rollback' subcommand with the given subparsers."""
    p = subparsers.add_parser("rollback", help="Revert to a previous snapshot")
    p.add_argument("dest", help="Destination snapshot file to overwrite")
    p.add_argument("--label", default=None, help="Roll back to the snapshot with this label")
    p.add_argument("--index", type=int, default=-1,
                   help="History index to roll back to (default: -1 = most recent)")
    p.add_argument("--dry-run", action="store_true", default=False,
                   help="Show what would change without writing anything")
    p.add_argument("--history-file", default=str(DEFAULT_HISTORY),
                   help="Path to the history JSON-lines file")
    p.set_defaults(func=cmd_rollback)
