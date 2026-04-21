"""Filter snapshots by key patterns, prefixes, or value conditions."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, List, Optional

Snapshot = Dict[str, str]


def filter_by_keys(snapshot: Snapshot, patterns: List[str]) -> Snapshot:
    """Return a new snapshot containing only keys that match any of the given glob patterns."""
    result = {}
    for key, value in snapshot.items():
        if any(fnmatch.fnmatch(key, pattern) for pattern in patterns):
            result[key] = value
    return result


def filter_by_prefix(snapshot: Snapshot, prefix: str) -> Snapshot:
    """Return a new snapshot containing only keys that start with *prefix*."""
    return {k: v for k, v in snapshot.items() if k.startswith(prefix)}


def filter_by_value_pattern(snapshot: Snapshot, pattern: str) -> Snapshot:
    """Return a new snapshot containing only entries whose value matches *pattern* (regex)."""
    compiled = re.compile(pattern)
    return {k: v for k, v in snapshot.items() if compiled.search(v)}


def exclude_keys(snapshot: Snapshot, patterns: List[str]) -> Snapshot:
    """Return a new snapshot with keys matching any of the given glob patterns removed."""
    result = {}
    for key, value in snapshot.items():
        if not any(fnmatch.fnmatch(key, pattern) for pattern in patterns):
            result[key] = value
    return result


def filter_snapshot(
    snapshot: Snapshot,
    *,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    prefix: Optional[str] = None,
    value_pattern: Optional[str] = None,
) -> Snapshot:
    """Convenience wrapper that applies multiple filter operations in sequence.

    Operations are applied in this order:
    1. include (glob key whitelist)
    2. exclude (glob key blacklist)
    3. prefix filter
    4. value_pattern (regex on values)
    """
    result = dict(snapshot)
    if include:
        result = filter_by_keys(result, include)
    if exclude:
        result = exclude_keys(result, exclude)
    if prefix is not None:
        result = filter_by_prefix(result, prefix)
    if value_pattern is not None:
        result = filter_by_value_pattern(result, value_pattern)
    return result
