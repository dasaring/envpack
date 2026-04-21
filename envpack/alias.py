"""Snapshot alias management — assign human-readable names to snapshot files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

_DEFAULT_ALIAS_FILE = Path(".envpack_aliases.json")


def _load_aliases(alias_file: Path) -> Dict[str, str]:
    if not alias_file.exists():
        return {}
    with alias_file.open() as fh:
        return json.load(fh)


def _save_aliases(aliases: Dict[str, str], alias_file: Path) -> None:
    with alias_file.open("w") as fh:
        json.dump(aliases, fh, indent=2)


def add_alias(
    name: str,
    snapshot_path: str,
    alias_file: Path = _DEFAULT_ALIAS_FILE,
) -> bool:
    """Register *name* as an alias for *snapshot_path*.

    Returns True if the alias was newly created, False if it was updated.
    """
    aliases = _load_aliases(alias_file)
    is_new = name not in aliases
    aliases[name] = snapshot_path
    _save_aliases(aliases, alias_file)
    return is_new


def remove_alias(name: str, alias_file: Path = _DEFAULT_ALIAS_FILE) -> bool:
    """Remove *name* from the alias registry.

    Returns True on success, False if the alias did not exist.
    """
    aliases = _load_aliases(alias_file)
    if name not in aliases:
        return False
    del aliases[name]
    _save_aliases(aliases, alias_file)
    return True


def resolve_alias(
    name: str, alias_file: Path = _DEFAULT_ALIAS_FILE
) -> Optional[str]:
    """Return the snapshot path for *name*, or None if not found."""
    return _load_aliases(alias_file).get(name)


def list_aliases(alias_file: Path = _DEFAULT_ALIAS_FILE) -> Dict[str, str]:
    """Return all registered aliases as {name: snapshot_path}."""
    return _load_aliases(alias_file)
