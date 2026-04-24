"""Rename or move snapshot files with optional metadata update."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


class RenameError(Exception):
    """Raised when a rename operation cannot be completed."""


def rename_snapshot(src: str | Path, dest: str | Path, *, overwrite: bool = False) -> Path:
    """Rename (move) a snapshot file from *src* to *dest*.

    Parameters
    ----------
    src:
        Path to the existing snapshot file.
    dest:
        Desired destination path.
    overwrite:
        If *True*, silently replace an existing file at *dest*.
        If *False* (default), raise :class:`RenameError` when *dest* already exists.

    Returns
    -------
    Path
        The resolved destination path.
    """
    src = Path(src)
    dest = Path(dest)

    if not src.exists():
        raise RenameError(f"Source snapshot not found: {src}")

    if not src.is_file():
        raise RenameError(f"Source is not a file: {src}")

    if dest.exists() and not overwrite:
        raise RenameError(
            f"Destination already exists: {dest}. Use overwrite=True to replace it."
        )

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    return dest.resolve()


def safe_rename(src: str | Path, dest: str | Path) -> tuple[bool, str]:
    """Attempt to rename *src* to *dest*, returning a (success, message) tuple.

    This is a convenience wrapper around :func:`rename_snapshot` that never
    raises — useful for CLI command handlers.
    """
    try:
        final = rename_snapshot(src, dest)
        return True, str(final)
    except RenameError as exc:
        return False, str(exc)
