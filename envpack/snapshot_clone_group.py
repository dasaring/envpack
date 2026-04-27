"""Snapshot clone group: manage named groups of related snapshot clones."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_STORE = Path(".envpack") / "clone_groups.json"


def _load_groups(store: Path) -> Dict[str, dict]:
    if not store.exists():
        return {}
    with store.open() as fh:
        return json.load(fh)


def _save_groups(data: Dict[str, dict], store: Path) -> None:
    store.parent.mkdir(parents=True, exist_ok=True)
    with store.open("w") as fh:
        json.dump(data, fh, indent=2)


def create_group(
    name: str,
    description: str = "",
    store: Path = _DEFAULT_STORE,
) -> dict:
    """Create a new clone group, overwriting any existing group with the same name."""
    data = _load_groups(store)
    entry = {"name": name, "description": description, "snapshots": []}
    data[name] = entry
    _save_groups(data, store)
    return entry


def delete_group(name: str, store: Path = _DEFAULT_STORE) -> bool:
    """Delete a clone group. Returns True if it existed."""
    data = _load_groups(store)
    if name not in data:
        return False
    del data[name]
    _save_groups(data, store)
    return True


def add_snapshot_to_group(
    name: str, snapshot_path: str, store: Path = _DEFAULT_STORE
) -> bool:
    """Add a snapshot path to a group. Returns False if already present."""
    data = _load_groups(store)
    if name not in data:
        raise KeyError(f"Clone group '{name}' does not exist.")
    if snapshot_path in data[name]["snapshots"]:
        return False
    data[name]["snapshots"].append(snapshot_path)
    _save_groups(data, store)
    return True


def remove_snapshot_from_group(
    name: str, snapshot_path: str, store: Path = _DEFAULT_STORE
) -> bool:
    """Remove a snapshot path from a group. Returns False if not present."""
    data = _load_groups(store)
    if name not in data:
        raise KeyError(f"Clone group '{name}' does not exist.")
    if snapshot_path not in data[name]["snapshots"]:
        return False
    data[name]["snapshots"].remove(snapshot_path)
    _save_groups(data, store)
    return True


def get_group(name: str, store: Path = _DEFAULT_STORE) -> Optional[dict]:
    """Return the group entry or None if not found."""
    return _load_groups(store).get(name)


def list_groups(store: Path = _DEFAULT_STORE) -> List[dict]:
    """Return all clone groups as a list."""
    return list(_load_groups(store).values())
