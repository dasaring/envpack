"""Checkpoint support: named save-points that bundle a snapshot path with metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envpack.audit import log_event

_DEFAULT_FILE = Path(".envpack_checkpoints.json")


def _load_checkpoints(store: Path) -> dict[str, Any]:
    if not store.exists():
        return {}
    return json.loads(store.read_text())


def _save_checkpoints(store: Path, data: dict[str, Any]) -> None:
    store.write_text(json.dumps(data, indent=2))


def create_checkpoint(
    name: str,
    snapshot_path: str,
    description: str = "",
    store: Path = _DEFAULT_FILE,
) -> dict[str, Any]:
    """Create or overwrite a named checkpoint."""
    checkpoints = _load_checkpoints(store)
    entry = {"snapshot": snapshot_path, "description": description}
    checkpoints[name] = entry
    _save_checkpoints(store, checkpoints)
    log_event("checkpoint_created", {"name": name, "snapshot": snapshot_path})
    return entry


def delete_checkpoint(name: str, store: Path = _DEFAULT_FILE) -> bool:
    """Delete a checkpoint by name. Returns True if it existed."""
    checkpoints = _load_checkpoints(store)
    if name not in checkpoints:
        return False
    del checkpoints[name]
    _save_checkpoints(store, checkpoints)
    log_event("checkpoint_deleted", {"name": name})
    return True


def get_checkpoint(name: str, store: Path = _DEFAULT_FILE) -> dict[str, Any] | None:
    """Return checkpoint entry or None if not found."""
    return _load_checkpoints(store).get(name)


def list_checkpoints(store: Path = _DEFAULT_FILE) -> dict[str, Any]:
    """Return all checkpoints."""
    return _load_checkpoints(store)
