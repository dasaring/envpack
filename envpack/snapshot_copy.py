"""snapshot_copy.py — copy/clone a snapshot file with optional key filtering and renaming."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable

from envpack.snapshot import load, save


class CopyError(Exception):
    """Raised when a snapshot copy operation fails."""


def copy_snapshot(
    src: str | Path,
    dest: str | Path,
    *,
    include_keys: Iterable[str] | None = None,
    exclude_keys: Iterable[str] | None = None,
    overwrite: bool = False,
) -> Path:
    """Copy *src* snapshot to *dest*, optionally filtering keys.

    Parameters
    ----------
    src:          Path to the source snapshot JSON file.
    dest:         Destination path for the copied snapshot.
    include_keys: If given, only these keys are kept in the copy.
    exclude_keys: If given, these keys are removed from the copy.
    overwrite:    Allow overwriting an existing destination file.

    Returns
    -------
    The resolved destination ``Path``.
    """
    src = Path(src)
    dest = Path(dest)

    if not src.exists():
        raise CopyError(f"Source snapshot not found: {src}")

    if dest.exists() and not overwrite:
        raise CopyError(
            f"Destination already exists: {dest}. Use overwrite=True to replace it."
        )

    # Fast path — no filtering needed
    if include_keys is None and exclude_keys is None:
        shutil.copy2(src, dest)
        return dest.resolve()

    data = load(src)

    if include_keys is not None:
        keep = set(include_keys)
        data = {k: v for k, v in data.items() if k in keep}

    if exclude_keys is not None:
        drop = set(exclude_keys)
        data = {k: v for k, v in data.items() if k not in drop}

    save(data, dest)
    return dest.resolve()


def clone_snapshot(src: str | Path, dest: str | Path, overwrite: bool = False) -> Path:
    """Convenience wrapper: copy all keys from *src* to *dest*."""
    return copy_snapshot(src, dest, overwrite=overwrite)
