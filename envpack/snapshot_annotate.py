"""Attach and retrieve free-form annotations (key/value metadata) on snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_DEFAULT_STORE = Path(".envpack") / "annotations.json"


def _load_annotations(store: Path) -> Dict[str, Dict[str, str]]:
    if store.exists():
        return json.loads(store.read_text())
    return {}


def _save_annotations(data: Dict[str, Dict[str, str]], store: Path) -> None:
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps(data, indent=2))


def annotate(
    snapshot_path: str,
    key: str,
    value: str,
    store: Path = _DEFAULT_STORE,
) -> bool:
    """Add or update an annotation on a snapshot. Returns True if new, False if updated."""
    data = _load_annotations(store)
    entry = data.setdefault(snapshot_path, {})
    is_new = key not in entry
    entry[key] = value
    _save_annotations(data, store)
    return is_new


def remove_annotation(
    snapshot_path: str,
    key: str,
    store: Path = _DEFAULT_STORE,
) -> bool:
    """Remove a single annotation key. Returns True if removed, False if not found."""
    data = _load_annotations(store)
    entry = data.get(snapshot_path, {})
    if key not in entry:
        return False
    del entry[key]
    if not entry:
        data.pop(snapshot_path, None)
    _save_annotations(data, store)
    return True


def get_annotations(
    snapshot_path: str,
    store: Path = _DEFAULT_STORE,
) -> Dict[str, str]:
    """Return all annotations for a snapshot (empty dict if none)."""
    data = _load_annotations(store)
    return dict(data.get(snapshot_path, {}))


def find_by_annotation(
    key: str,
    value: Optional[str] = None,
    store: Path = _DEFAULT_STORE,
) -> Dict[str, str]:
    """Find snapshots that have a given annotation key (optionally matching value).

    Returns a mapping of snapshot_path -> annotation_value.
    """
    data = _load_annotations(store)
    results: Dict[str, str] = {}
    for snap, annotations in data.items():
        if key in annotations:
            if value is None or annotations[key] == value:
                results[snap] = annotations[key]
    return results


def clear_annotations(
    snapshot_path: str,
    store: Path = _DEFAULT_STORE,
) -> int:
    """Remove all annotations for a snapshot. Returns number of keys removed."""
    data = _load_annotations(store)
    entry = data.pop(snapshot_path, {})
    if entry:
        _save_annotations(data, store)
    return len(entry)
