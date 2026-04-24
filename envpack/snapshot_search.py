"""Search snapshots by key presence, value pattern, or metadata."""

from __future__ import annotations

import fnmatch
import json
import os
from dataclasses import dataclass, field
from typing import List, Optional

from envpack.snapshot import load


@dataclass
class SearchResult:
    path: str
    matched_keys: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"path": self.path, "matched_keys": self.matched_keys}


def search_by_key(directory: str, key_pattern: str) -> List[SearchResult]:
    """Return snapshots in *directory* that contain a key matching *key_pattern*."""
    results = []
    for fname in sorted(os.listdir(directory)):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(directory, fname)
        try:
            snapshot = load(fpath)
        except (json.JSONDecodeError, KeyError, OSError):
            continue
        matched = [k for k in snapshot if fnmatch.fnmatch(k, key_pattern)]
        if matched:
            results.append(SearchResult(path=fpath, matched_keys=matched))
    return results


def search_by_value(directory: str, value_pattern: str) -> List[SearchResult]:
    """Return snapshots whose values contain a substring matching *value_pattern*."""
    results = []
    for fname in sorted(os.listdir(directory)):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(directory, fname)
        try:
            snapshot = load(fpath)
        except (json.JSONDecodeError, KeyError, OSError):
            continue
        matched = [
            k for k, v in snapshot.items() if fnmatch.fnmatch(str(v), value_pattern)
        ]
        if matched:
            results.append(SearchResult(path=fpath, matched_keys=matched))
    return results


def search_snapshots(
    directory: str,
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
) -> List[SearchResult]:
    """Unified search: filter by key pattern and/or value pattern."""
    if not key_pattern and not value_pattern:
        raise ValueError("At least one of key_pattern or value_pattern must be given.")
    if key_pattern and not value_pattern:
        return search_by_key(directory, key_pattern)
    if value_pattern and not key_pattern:
        return search_by_value(directory, value_pattern)
    # Both specified — intersection
    by_key = {r.path: r for r in search_by_key(directory, key_pattern)}
    by_val = {r.path: r for r in search_by_value(directory, value_pattern)}
    combined = []
    for path in sorted(set(by_key) & set(by_val)):
        merged_keys = sorted(set(by_key[path].matched_keys) & set(by_val[path].matched_keys))
        combined.append(SearchResult(path=path, matched_keys=merged_keys))
    return combined
