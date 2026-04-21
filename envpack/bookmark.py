"""Bookmark module: assign friendly short names to snapshot paths."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_DEFAULT_STORE = Path.home() / ".envpack" / "bookmarks.json"


def _load_bookmarks(store: Path) -> Dict[str, str]:
    if store.exists():
        return json.loads(store.read_text())
    return {}


def _save_bookmarks(bookmarks: Dict[str, str], store: Path) -> None:
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps(bookmarks, indent=2))


def add_bookmark(name: str, snapshot_path: str, store: Path = _DEFAULT_STORE) -> bool:
    """Add or update a bookmark. Returns True if new, False if updated."""
    bookmarks = _load_bookmarks(store)
    is_new = name not in bookmarks
    bookmarks[name] = str(snapshot_path)
    _save_bookmarks(bookmarks, store)
    return is_new


def remove_bookmark(name: str, store: Path = _DEFAULT_STORE) -> bool:
    """Remove a bookmark by name. Returns True if removed, False if not found."""
    bookmarks = _load_bookmarks(store)
    if name not in bookmarks:
        return False
    del bookmarks[name]
    _save_bookmarks(bookmarks, store)
    return True


def resolve_bookmark(name: str, store: Path = _DEFAULT_STORE) -> Optional[str]:
    """Return the snapshot path for a bookmark name, or None if not found."""
    return _load_bookmarks(store).get(name)


def list_bookmarks(store: Path = _DEFAULT_STORE) -> Dict[str, str]:
    """Return all bookmarks as a dict of {name: path}."""
    return _load_bookmarks(store)


def clear_bookmarks(store: Path = _DEFAULT_STORE) -> int:
    """Remove all bookmarks. Returns the number of bookmarks cleared."""
    bookmarks = _load_bookmarks(store)
    count = len(bookmarks)
    _save_bookmarks({}, store)
    return count
