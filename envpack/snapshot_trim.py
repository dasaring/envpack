"""snapshot_trim.py — remove keys from a snapshot by pattern or list."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Iterable

from envpack.snapshot import load, save


class TrimError(Exception):
    """Raised when trimming fails."""


def trim_by_keys(snapshot: dict, keys: Iterable[str]) -> dict:
    """Return a new snapshot with the given exact keys removed."""
    remove = set(keys)
    return {k: v for k, v in snapshot.items() if k not in remove}


def trim_by_prefix(snapshot: dict, prefix: str) -> dict:
    """Return a new snapshot with all keys starting with *prefix* removed."""
    return {k: v for k, v in snapshot.items() if not k.startswith(prefix)}


def trim_by_pattern(snapshot: dict, pattern: str) -> dict:
    """Return a new snapshot with all keys matching *pattern* (glob) removed."""
    return {k: v for k, v in snapshot.items() if not fnmatch.fnmatch(k, pattern)}


def trim_snapshot(
    snapshot: dict,
    *,
    keys: Iterable[str] | None = None,
    prefix: str | None = None,
    pattern: str | None = None,
) -> dict:
    """Apply one or more trim operations and return the resulting snapshot.

    At least one of *keys*, *prefix*, or *pattern* must be supplied.
    Operations are applied in order: keys → prefix → pattern.
    """
    if keys is None and prefix is None and pattern is None:
        raise TrimError("At least one of keys, prefix, or pattern must be provided.")

    result = dict(snapshot)
    if keys is not None:
        result = trim_by_keys(result, keys)
    if prefix is not None:
        result = trim_by_prefix(result, prefix)
    if pattern is not None:
        result = trim_by_pattern(result, pattern)
    return result


def trim_file(
    src: Path,
    dest: Path,
    *,
    keys: Iterable[str] | None = None,
    prefix: str | None = None,
    pattern: str | None = None,
) -> Path:
    """Load *src*, trim it, and save the result to *dest*. Returns *dest*."""
    snapshot = load(src)
    trimmed = trim_snapshot(snapshot, keys=keys, prefix=prefix, pattern=pattern)
    save(trimmed, dest)
    return dest
