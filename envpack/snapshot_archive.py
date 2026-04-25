"""Archive and unarchive snapshots — move them out of active use without deleting."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import List, Optional

_DEFAULT_ARCHIVE_DIR = Path(".envpack_archive")


class ArchiveError(Exception):
    pass


def archive_snapshot(source: Path, archive_dir: Path = _DEFAULT_ARCHIVE_DIR) -> Path:
    """Move *source* into *archive_dir*. Returns the destination path."""
    source = Path(source)
    if not source.exists():
        raise ArchiveError(f"Snapshot not found: {source}")

    archive_dir = Path(archive_dir)
    archive_dir.mkdir(parents=True, exist_ok=True)

    dest = archive_dir / source.name
    if dest.exists():
        raise ArchiveError(f"Archive already contains a file named '{source.name}'")

    shutil.move(str(source), str(dest))
    return dest


def unarchive_snapshot(
    name: str,
    dest_dir: Path,
    archive_dir: Path = _DEFAULT_ARCHIVE_DIR,
    overwrite: bool = False,
) -> Path:
    """Restore an archived snapshot back to *dest_dir*."""
    archive_dir = Path(archive_dir)
    src = archive_dir / name
    if not src.exists():
        raise ArchiveError(f"No archived snapshot named '{name}'")

    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / name

    if dest.exists() and not overwrite:
        raise ArchiveError(f"Destination already exists: {dest}. Use overwrite=True.")

    shutil.move(str(src), str(dest))
    return dest


def list_archived(archive_dir: Path = _DEFAULT_ARCHIVE_DIR) -> List[str]:
    """Return names of all archived snapshot files."""
    archive_dir = Path(archive_dir)
    if not archive_dir.exists():
        return []
    return sorted(p.name for p in archive_dir.iterdir() if p.suffix == ".json")


def is_archived(name: str, archive_dir: Path = _DEFAULT_ARCHIVE_DIR) -> bool:
    """Return True if *name* exists in the archive directory."""
    return (Path(archive_dir) / name).exists()
