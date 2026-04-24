"""Apply patch operations (set, unset, rename) to a snapshot file."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from envpack.snapshot import load, save


class PatchError(Exception):
    """Raised when a patch operation cannot be applied."""


def set_keys(snapshot: Dict[str, str], updates: Dict[str, str]) -> Dict[str, str]:
    """Return a new snapshot with *updates* applied (add or overwrite keys)."""
    result = dict(snapshot)
    result.update(updates)
    return result


def unset_keys(snapshot: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Return a new snapshot with *keys* removed (missing keys are ignored)."""
    return {k: v for k, v in snapshot.items() if k not in keys}


def rename_key(
    snapshot: Dict[str, str], old_key: str, new_key: str, *, overwrite: bool = False
) -> Dict[str, str]:
    """Return a new snapshot with *old_key* renamed to *new_key*.

    Raises PatchError if *old_key* does not exist, or if *new_key* already
    exists and *overwrite* is False.
    """
    if old_key not in snapshot:
        raise PatchError(f"Key not found: {old_key!r}")
    if new_key in snapshot and not overwrite:
        raise PatchError(
            f"Key {new_key!r} already exists. Use overwrite=True to replace it."
        )
    result = {(new_key if k == old_key else k): v for k, v in snapshot.items()}
    return result


def patch_file(
    path: Path,
    *,
    set: Optional[Dict[str, str]] = None,
    unset: Optional[List[str]] = None,
    rename: Optional[Dict[str, str]] = None,
    overwrite_rename: bool = False,
    dest: Optional[Path] = None,
) -> Path:
    """Load *path*, apply patch operations, and save the result.

    Parameters
    ----------
    set:            key/value pairs to add or overwrite.
    unset:          keys to remove.
    rename:         mapping of {old_key: new_key}.
    overwrite_rename: allow rename to clobber an existing key.
    dest:           output path; defaults to *path* (in-place).

    Returns the path that was written.
    """
    snapshot = load(path)

    if set:
        snapshot = set_keys(snapshot, set)
    if unset:
        snapshot = unset_keys(snapshot, unset)
    if rename:
        for old, new in rename.items():
            snapshot = rename_key(snapshot, old, new, overwrite=overwrite_rename)

    out = dest or path
    save(snapshot, out)
    return out
