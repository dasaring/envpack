"""Mask specific keys in a snapshot with a configurable placeholder."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Iterable, Optional

DEFAULT_MASK = "***"


class MaskError(Exception):
    """Raised when masking fails."""


def mask_by_keys(
    snapshot: Dict[str, str],
    keys: Iterable[str],
    mask: str = DEFAULT_MASK,
) -> Dict[str, str]:
    """Return a new snapshot with exact *keys* replaced by *mask*."""
    keys_set = set(keys)
    return {k: (mask if k in keys_set else v) for k, v in snapshot.items()}


def mask_by_pattern(
    snapshot: Dict[str, str],
    pattern: str,
    mask: str = DEFAULT_MASK,
) -> Dict[str, str]:
    """Return a new snapshot with keys matching *pattern* (regex) replaced by *mask*."""
    try:
        rx = re.compile(pattern)
    except re.error as exc:
        raise MaskError(f"Invalid pattern {pattern!r}: {exc}") from exc
    return {k: (mask if rx.search(k) else v) for k, v in snapshot.items()}


def masked_keys(
    snapshot: Dict[str, str],
    mask: str = DEFAULT_MASK,
) -> list[str]:
    """Return the list of keys whose value equals *mask*."""
    return [k for k, v in snapshot.items() if v == mask]


def mask_file(
    path: Path | str,
    keys: Optional[Iterable[str]] = None,
    pattern: Optional[str] = None,
    mask: str = DEFAULT_MASK,
    output: Optional[Path | str] = None,
) -> Path:
    """Load a snapshot file, mask it, and write the result.

    If *output* is None the source file is overwritten.
    Returns the path that was written.
    """
    path = Path(path)
    if not path.exists():
        raise MaskError(f"Snapshot file not found: {path}")

    with path.open() as fh:
        snapshot: Dict[str, str] = json.load(fh)

    if keys is not None:
        snapshot = mask_by_keys(snapshot, keys, mask)
    if pattern is not None:
        snapshot = mask_by_pattern(snapshot, pattern, mask)

    dest = Path(output) if output else path
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w") as fh:
        json.dump(snapshot, fh, indent=2, sort_keys=True)

    return dest
