"""snapshot_expire.py — mark snapshots with an expiry date and check if they are expired."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

_EXPIRY_FILE_DEFAULT = ".envpack_expiry.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_expiry(store: Path) -> Dict[str, str]:
    if store.exists():
        return json.loads(store.read_text())
    return {}


def _save_expiry(store: Path, data: Dict[str, str]) -> None:
    store.write_text(json.dumps(data, indent=2))


def set_expiry(snapshot_path: str, expires_at: str, store: Optional[Path] = None) -> bool:
    """Set an ISO-8601 expiry date for a snapshot. Returns True if newly set, False if updated."""
    store = store or Path(_EXPIRY_FILE_DEFAULT)
    data = _load_expiry(store)
    is_new = snapshot_path not in data
    data[snapshot_path] = expires_at
    _save_expiry(store, data)
    return is_new


def remove_expiry(snapshot_path: str, store: Optional[Path] = None) -> bool:
    """Remove expiry for a snapshot. Returns True if it existed, False otherwise."""
    store = store or Path(_EXPIRY_FILE_DEFAULT)
    data = _load_expiry(store)
    if snapshot_path not in data:
        return False
    del data[snapshot_path]
    _save_expiry(store, data)
    return True


def get_expiry(snapshot_path: str, store: Optional[Path] = None) -> Optional[str]:
    """Return the ISO-8601 expiry string for a snapshot, or None."""
    store = store or Path(_EXPIRY_FILE_DEFAULT)
    return _load_expiry(store).get(snapshot_path)


def is_expired(snapshot_path: str, store: Optional[Path] = None) -> bool:
    """Return True if the snapshot's expiry date is in the past."""
    expiry = get_expiry(snapshot_path, store)
    if expiry is None:
        return False
    expiry_dt = datetime.fromisoformat(expiry)
    now = datetime.now(timezone.utc)
    if expiry_dt.tzinfo is None:
        expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)
    return now > expiry_dt


def list_expired(store: Optional[Path] = None) -> List[str]:
    """Return a list of snapshot paths whose expiry date has passed."""
    store = store or Path(_EXPIRY_FILE_DEFAULT)
    data = _load_expiry(store)
    return [path for path in data if is_expired(path, store)]


def list_all(store: Optional[Path] = None) -> Dict[str, str]:
    """Return all snapshot -> expiry mappings."""
    store = store or Path(_EXPIRY_FILE_DEFAULT)
    return dict(_load_expiry(store))
