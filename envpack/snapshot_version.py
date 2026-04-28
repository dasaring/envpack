"""Snapshot versioning: track multiple named versions of a snapshot path."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_STORE = Path(".envpack_versions.json")


class VersionError(Exception):
    pass


def _load_versions(store: Path) -> Dict[str, List[dict]]:
    if not store.exists():
        return {}
    with store.open() as fh:
        return json.load(fh)


def _save_versions(data: Dict[str, List[dict]], store: Path) -> None:
    store.parent.mkdir(parents=True, exist_ok=True)
    with store.open("w") as fh:
        json.dump(data, fh, indent=2)


def add_version(
    name: str,
    snapshot_path: str,
    label: Optional[str] = None,
    store: Path = _DEFAULT_STORE,
) -> dict:
    """Record a new version entry under *name*. Returns the new entry."""
    data = _load_versions(store)
    entry = {"snapshot": snapshot_path, "label": label}
    data.setdefault(name, []).append(entry)
    _save_versions(data, store)
    return entry


def list_versions(name: str, store: Path = _DEFAULT_STORE) -> List[dict]:
    """Return all version entries for *name*, oldest first."""
    data = _load_versions(store)
    return list(data.get(name, []))


def get_version(
    name: str, index: int = -1, store: Path = _DEFAULT_STORE
) -> Optional[dict]:
    """Return a specific version entry by index (default: latest)."""
    versions = list_versions(name, store)
    if not versions:
        return None
    try:
        return versions[index]
    except IndexError:
        return None


def delete_version_history(name: str, store: Path = _DEFAULT_STORE) -> bool:
    """Remove all version history for *name*. Returns True if it existed."""
    data = _load_versions(store)
    if name not in data:
        return False
    del data[name]
    _save_versions(data, store)
    return True


def all_version_names(store: Path = _DEFAULT_STORE) -> List[str]:
    """Return all tracked version names."""
    return list(_load_versions(store).keys())
