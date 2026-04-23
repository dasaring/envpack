"""Label management for envpack snapshots.

Allows assigning human-readable labels to snapshot file paths,
listing all labels, and resolving a label back to its path.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_STORE = Path(".envpack") / "labels.json"


def _load_labels(store: Path) -> Dict[str, str]:
    if store.exists():
        return json.loads(store.read_text())
    return {}


def _save_labels(data: Dict[str, str], store: Path) -> None:
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps(data, indent=2))


def add_label(label: str, snapshot_path: str, store: Path = _DEFAULT_STORE) -> bool:
    """Associate *label* with *snapshot_path*.

    Returns True if the label is new, False if it was updated.
    """
    data = _load_labels(store)
    is_new = label not in data
    data[label] = snapshot_path
    _save_labels(data, store)
    return is_new


def remove_label(label: str, store: Path = _DEFAULT_STORE) -> bool:
    """Remove *label*. Returns True on success, False if not found."""
    data = _load_labels(store)
    if label not in data:
        return False
    del data[label]
    _save_labels(data, store)
    return True


def resolve_label(label: str, store: Path = _DEFAULT_STORE) -> Optional[str]:
    """Return the snapshot path for *label*, or None if not found."""
    return _load_labels(store).get(label)


def list_labels(store: Path = _DEFAULT_STORE) -> List[Dict[str, str]]:
    """Return all labels as a list of {label, path} dicts."""
    data = _load_labels(store)
    return [{"label": k, "path": v} for k, v in sorted(data.items())]
