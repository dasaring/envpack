"""Track and manage snapshot history with timestamps and metadata."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

DEFAULT_HISTORY_FILE = ".envpack_history.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_history(history_file: str) -> List[dict]:
    path = Path(history_file)
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_history(entries: List[dict], history_file: str) -> None:
    with open(history_file, "w") as f:
        json.dump(entries, f, indent=2)


def record_snapshot(
    snapshot_path: str,
    label: Optional[str] = None,
    history_file: str = DEFAULT_HISTORY_FILE,
) -> dict:
    """Record a snapshot path and optional label in history."""
    entries = _load_history(history_file)
    entry = {
        "snapshot_path": snapshot_path,
        "label": label,
        "recorded_at": _now_iso(),
    }
    entries.append(entry)
    _save_history(entries, history_file)
    return entry


def list_history(history_file: str = DEFAULT_HISTORY_FILE) -> List[dict]:
    """Return all history entries."""
    return _load_history(history_file)


def find_by_label(label: str, history_file: str = DEFAULT_HISTORY_FILE) -> List[dict]:
    """Return entries matching a given label."""
    return [e for e in _load_history(history_file) if e.get("label") == label]


def remove_entry(snapshot_path: str, history_file: str = DEFAULT_HISTORY_FILE) -> bool:
    """Remove a history entry by snapshot path. Returns True if removed."""
    entries = _load_history(history_file)
    new_entries = [e for e in entries if e["snapshot_path"] != snapshot_path]
    if len(new_entries) == len(entries):
        return False
    _save_history(new_entries, history_file)
    return True


def clear_history(history_file: str = DEFAULT_HISTORY_FILE) -> None:
    """Clear all history entries."""
    _save_history([], history_file)
