"""Track parent-child lineage relationships between snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_STORE = Path(".envpack") / "lineage.json"


def _load_lineage(store: Path) -> Dict[str, str]:
    """Return mapping of snapshot_path -> parent_path."""
    if not store.exists():
        return {}
    return json.loads(store.read_text())


def _save_lineage(data: Dict[str, str], store: Path) -> None:
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps(data, indent=2))


def set_parent(snapshot: str, parent: str, store: Path = _DEFAULT_STORE) -> bool:
    """Record *parent* as the parent of *snapshot*. Returns True if new."""
    data = _load_lineage(store)
    is_new = snapshot not in data
    data[snapshot] = parent
    _save_lineage(data, store)
    return is_new


def remove_parent(snapshot: str, store: Path = _DEFAULT_STORE) -> bool:
    """Remove lineage record for *snapshot*. Returns True if it existed."""
    data = _load_lineage(store)
    if snapshot not in data:
        return False
    del data[snapshot]
    _save_lineage(data, store)
    return True


def get_parent(snapshot: str, store: Path = _DEFAULT_STORE) -> Optional[str]:
    """Return the parent path for *snapshot*, or None."""
    return _load_lineage(store).get(snapshot)


def get_children(parent: str, store: Path = _DEFAULT_STORE) -> List[str]:
    """Return all snapshots whose parent is *parent*."""
    data = _load_lineage(store)
    return [snap for snap, p in data.items() if p == parent]


def ancestors(snapshot: str, store: Path = _DEFAULT_STORE) -> List[str]:
    """Return ordered list of ancestors, oldest last."""
    data = _load_lineage(store)
    chain: List[str] = []
    current = snapshot
    seen = set()
    while current in data:
        parent = data[current]
        if parent in seen:
            break
        seen.add(parent)
        chain.append(parent)
        current = parent
    return chain


def list_lineage(store: Path = _DEFAULT_STORE) -> Dict[str, str]:
    """Return the full lineage mapping."""
    return _load_lineage(store)
