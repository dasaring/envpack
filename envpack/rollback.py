"""Rollback support: revert to a previous snapshot from history."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from envpack.history import list_history, find_by_label
from envpack.snapshot import load, save
from envpack.diff import compute_diff


class RollbackError(Exception):
    """Raised when a rollback cannot be completed."""


def get_rollback_target(history_file: Path, label: Optional[str] = None, index: int = -1) -> dict:
    """Return a history entry to roll back to.

    If *label* is given, search by label; otherwise use *index* (default -1 = most recent).
    """
    if label:
        entry = find_by_label(label, history_file=history_file)
        if entry is None:
            raise RollbackError(f"No history entry with label {label!r}")
        return entry

    entries = list_history(history_file=history_file)
    if not entries:
        raise RollbackError("History is empty; nothing to roll back to")
    try:
        return entries[index]
    except IndexError:
        raise RollbackError(f"History index {index} is out of range (have {len(entries)} entries)")


def rollback(target_path: str, dest_path: str, *, dry_run: bool = False) -> dict:
    """Copy the snapshot at *target_path* to *dest_path*.

    Returns a dict with keys:
      - 'source': path that was rolled back to
      - 'dest': path that was written
      - 'diff': DiffResult between old dest (if it exists) and new snapshot
      - 'dry_run': bool
    """
    new_snapshot = load(target_path)

    old_snapshot = {}
    if os.path.exists(dest_path):
        try:
            old_snapshot = load(dest_path)
        except Exception:
            old_snapshot = {}

    diff = compute_diff(old_snapshot, new_snapshot)

    if not dry_run:
        save(new_snapshot, dest_path)

    return {
        "source": target_path,
        "dest": dest_path,
        "diff": diff,
        "dry_run": dry_run,
    }
