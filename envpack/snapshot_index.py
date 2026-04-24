"""snapshot_index.py — build and query an in-memory index of snapshot files.

An index maps a directory of .json snapshot files to a lightweight
catalogue entry (path, captured_at, key count, size in bytes) so other
modules can search / sort without loading every file.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional


@dataclass
class IndexEntry:
    path: str
    captured_at: Optional[str]
    key_count: int
    size_bytes: int

    def to_dict(self) -> dict:
        return asdict(self)


def _entry_from_file(filepath: Path) -> Optional[IndexEntry]:
    """Return an IndexEntry for *filepath*, or None if the file is not a valid snapshot."""
    try:
        raw = filepath.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict):
        return None

    return IndexEntry(
        path=str(filepath.resolve()),
        captured_at=data.get("captured_at"),
        key_count=len(data.get("env", data)),  # support both wrapped and flat snapshots
        size_bytes=len(raw.encode()),
    )


def build_index(directory: str) -> List[IndexEntry]:
    """Scan *directory* for *.json files and return a list of IndexEntry objects."""
    base = Path(directory)
    if not base.is_dir():
        raise NotADirectoryError(f"{directory!r} is not a directory")

    entries: List[IndexEntry] = []
    for fp in sorted(base.glob("*.json")):
        entry = _entry_from_file(fp)
        if entry is not None:
            entries.append(entry)
    return entries


def find_by_key(index: List[IndexEntry], key_name: str) -> List[IndexEntry]:
    """Return entries whose snapshot contains *key_name*."""
    matches = []
    for entry in index:
        try:
            data = json.loads(Path(entry.path).read_text(encoding="utf-8"))
            env = data.get("env", data)
            if key_name in env:
                matches.append(entry)
        except (OSError, json.JSONDecodeError):
            continue
    return matches


def largest(index: List[IndexEntry], n: int = 5) -> List[IndexEntry]:
    """Return the *n* largest snapshots by key count."""
    return sorted(index, key=lambda e: e.key_count, reverse=True)[:n]


def summary(index: List[IndexEntry]) -> str:
    total_keys = sum(e.key_count for e in index)
    total_bytes = sum(e.size_bytes for e in index)
    return (
        f"{len(index)} snapshot(s) indexed, "
        f"{total_keys} total keys, "
        f"{total_bytes} bytes on disk"
    )
