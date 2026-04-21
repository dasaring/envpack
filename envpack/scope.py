"""Scope support: group snapshots by named scope (e.g. project, team, env)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_SCOPE_FILE = Path(".envpack_scopes.json")


def _load_scopes(scope_file: Path) -> Dict[str, List[str]]:
    if not scope_file.exists():
        return {}
    with scope_file.open() as fh:
        return json.load(fh)


def _save_scopes(data: Dict[str, List[str]], scope_file: Path) -> None:
    with scope_file.open("w") as fh:
        json.dump(data, fh, indent=2)


def add_to_scope(
    scope: str,
    snapshot_path: str,
    scope_file: Path = DEFAULT_SCOPE_FILE,
) -> bool:
    """Add snapshot to scope. Returns True if newly added, False if already present."""
    data = _load_scopes(scope_file)
    entries = data.setdefault(scope, [])
    if snapshot_path in entries:
        return False
    entries.append(snapshot_path)
    _save_scopes(data, scope_file)
    return True


def remove_from_scope(
    scope: str,
    snapshot_path: str,
    scope_file: Path = DEFAULT_SCOPE_FILE,
) -> bool:
    """Remove snapshot from scope. Returns True if removed, False if not found."""
    data = _load_scopes(scope_file)
    entries = data.get(scope, [])
    if snapshot_path not in entries:
        return False
    entries.remove(snapshot_path)
    if not entries:
        del data[scope]
    _save_scopes(data, scope_file)
    return True


def list_scopes(scope_file: Path = DEFAULT_SCOPE_FILE) -> List[str]:
    """Return all scope names."""
    return list(_load_scopes(scope_file).keys())


def get_snapshots_in_scope(
    scope: str,
    scope_file: Path = DEFAULT_SCOPE_FILE,
) -> List[str]:
    """Return snapshot paths registered under a scope."""
    return _load_scopes(scope_file).get(scope, [])


def find_scope_for_snapshot(
    snapshot_path: str,
    scope_file: Path = DEFAULT_SCOPE_FILE,
) -> Optional[str]:
    """Return the first scope that contains the given snapshot, or None."""
    for scope, paths in _load_scopes(scope_file).items():
        if snapshot_path in paths:
            return scope
    return None
