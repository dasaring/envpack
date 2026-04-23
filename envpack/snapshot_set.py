"""snapshot_set.py — manage named collections (sets) of snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_STORE = Path(".envpack") / "snapshot_sets.json"


def _load_sets(store: Path) -> Dict[str, dict]:
    if store.exists():
        return json.loads(store.read_text())
    return {}


def _save_sets(data: Dict[str, dict], store: Path) -> None:
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps(data, indent=2))


def create_set(
    name: str,
    description: str = "",
    store: Path = _DEFAULT_STORE,
) -> dict:
    """Create a new (empty) snapshot set. Overwrites if exists."""
    data = _load_sets(store)
    entry = {"name": name, "description": description, "snapshots": []}
    data[name] = entry
    _save_sets(data, store)
    return entry


def delete_set(name: str, store: Path = _DEFAULT_STORE) -> bool:
    """Delete a set by name. Returns True if it existed."""
    data = _load_sets(store)
    if name not in data:
        return False
    del data[name]
    _save_sets(data, store)
    return True


def add_snapshot_to_set(
    name: str, snapshot_path: str, store: Path = _DEFAULT_STORE
) -> bool:
    """Add a snapshot path to a set. Returns False if already present."""
    data = _load_sets(store)
    if name not in data:
        raise KeyError(f"Snapshot set '{name}' does not exist.")
    if snapshot_path in data[name]["snapshots"]:
        return False
    data[name]["snapshots"].append(snapshot_path)
    _save_sets(data, store)
    return True


def remove_snapshot_from_set(
    name: str, snapshot_path: str, store: Path = _DEFAULT_STORE
) -> bool:
    """Remove a snapshot path from a set. Returns False if not present."""
    data = _load_sets(store)
    if name not in data:
        raise KeyError(f"Snapshot set '{name}' does not exist.")
    if snapshot_path not in data[name]["snapshots"]:
        return False
    data[name]["snapshots"].remove(snapshot_path)
    _save_sets(data, store)
    return True


def get_set(name: str, store: Path = _DEFAULT_STORE) -> Optional[dict]:
    """Return the set entry or None."""
    return _load_sets(store).get(name)


def list_sets(store: Path = _DEFAULT_STORE) -> List[dict]:
    """Return all sets as a list of dicts."""
    return list(_load_sets(store).values())
