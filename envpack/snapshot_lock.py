"""Snapshot locking — prevent accidental modification of important snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

_DEFAULT_LOCK_FILE = Path(".envpack_locks.json")


def _load_locks(lock_file: Path) -> Dict[str, str]:
    """Return mapping of snapshot_path -> reason."""
    if not lock_file.exists():
        return {}
    with lock_file.open() as f:
        return json.load(f)


def _save_locks(locks: Dict[str, str], lock_file: Path) -> None:
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    with lock_file.open("w") as f:
        json.dump(locks, f, indent=2)


def lock_snapshot(
    snapshot_path: str,
    reason: str = "",
    lock_file: Path = _DEFAULT_LOCK_FILE,
) -> bool:
    """Lock a snapshot. Returns True if newly locked, False if already locked."""
    locks = _load_locks(lock_file)
    key = str(snapshot_path)
    if key in locks:
        return False
    locks[key] = reason
    _save_locks(locks, lock_file)
    return True


def unlock_snapshot(
    snapshot_path: str,
    lock_file: Path = _DEFAULT_LOCK_FILE,
) -> bool:
    """Unlock a snapshot. Returns True if removed, False if was not locked."""
    locks = _load_locks(lock_file)
    key = str(snapshot_path)
    if key not in locks:
        return False
    del locks[key]
    _save_locks(locks, lock_file)
    return True


def is_locked(
    snapshot_path: str,
    lock_file: Path = _DEFAULT_LOCK_FILE,
) -> bool:
    """Return True if the snapshot is locked."""
    return str(snapshot_path) in _load_locks(lock_file)


def list_locks(lock_file: Path = _DEFAULT_LOCK_FILE) -> List[Dict[str, str]]:
    """Return all locked snapshots as a list of dicts with 'path' and 'reason'."""
    locks = _load_locks(lock_file)
    return [{"path": path, "reason": reason} for path, reason in locks.items()]


class SnapshotLockedError(Exception):
    """Raised when an operation is attempted on a locked snapshot."""
