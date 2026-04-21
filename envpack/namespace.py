"""Namespace support: group snapshots under named namespaces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_FILE = Path(".envpack_namespaces.json")


def _load_namespaces(ns_file: Path) -> Dict[str, List[str]]:
    if not ns_file.exists():
        return {}
    with ns_file.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_namespaces(data: Dict[str, List[str]], ns_file: Path) -> None:
    with ns_file.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def add_to_namespace(
    namespace: str,
    snapshot_path: str,
    ns_file: Path = _DEFAULT_FILE,
) -> bool:
    """Add *snapshot_path* to *namespace*. Returns True if newly added."""
    data = _load_namespaces(ns_file)
    entries = data.setdefault(namespace, [])
    if snapshot_path in entries:
        return False
    entries.append(snapshot_path)
    _save_namespaces(data, ns_file)
    return True


def remove_from_namespace(
    namespace: str,
    snapshot_path: str,
    ns_file: Path = _DEFAULT_FILE,
) -> bool:
    """Remove *snapshot_path* from *namespace*. Returns True if it existed."""
    data = _load_namespaces(ns_file)
    entries = data.get(namespace, [])
    if snapshot_path not in entries:
        return False
    entries.remove(snapshot_path)
    if not entries:
        del data[namespace]
    _save_namespaces(data, ns_file)
    return True


def list_namespaces(ns_file: Path = _DEFAULT_FILE) -> List[str]:
    """Return all namespace names."""
    return list(_load_namespaces(ns_file).keys())


def get_snapshots_in_namespace(
    namespace: str,
    ns_file: Path = _DEFAULT_FILE,
) -> List[str]:
    """Return snapshot paths registered under *namespace*."""
    return list(_load_namespaces(ns_file).get(namespace, []))


def find_namespace_for_snapshot(
    snapshot_path: str,
    ns_file: Path = _DEFAULT_FILE,
) -> Optional[str]:
    """Return the first namespace that contains *snapshot_path*, or None."""
    for ns, paths in _load_namespaces(ns_file).items():
        if snapshot_path in paths:
            return ns
    return None
