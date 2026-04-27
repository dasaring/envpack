"""Promote a snapshot from one environment stage to another."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

KNOWN_STAGES = ["dev", "staging", "production"]


class PromoteError(Exception):
    """Raised when a promotion fails."""


def _load(path: Path) -> dict:
    with open(path) as fh:
        return json.load(fh)


def _save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)


def promote_snapshot(
    source: Path,
    dest: Path,
    *,
    overwrite: bool = False,
    strip_keys: Optional[list[str]] = None,
    add_keys: Optional[dict[str, str]] = None,
) -> Path:
    """Copy *source* snapshot to *dest*, optionally transforming it.

    Parameters
    ----------
    source:      Path to the snapshot being promoted.
    dest:        Destination path for the promoted snapshot.
    overwrite:   Allow overwriting an existing destination file.
    strip_keys:  Keys to remove before writing to *dest*.
    add_keys:    Key/value pairs to inject into the promoted snapshot.

    Returns the resolved destination path.
    """
    source = Path(source)
    dest = Path(dest)

    if not source.exists():
        raise PromoteError(f"Source snapshot not found: {source}")

    if dest.exists() and not overwrite:
        raise PromoteError(
            f"Destination already exists: {dest}. Use overwrite=True to replace it."
        )

    data = _load(source)

    for key in strip_keys or []:
        data.pop(key, None)

    if add_keys:
        data.update(add_keys)

    _save(dest, data)
    return dest


def promotion_diff(source: Path, dest: Path) -> dict:
    """Return a summary of what would change when promoting *source* to *dest*.

    Returns a dict with keys ``added``, ``removed``, ``changed``, ``unchanged``.
    """
    source_data = _load(Path(source))
    dest_data = _load(Path(dest)) if Path(dest).exists() else {}

    all_keys = set(source_data) | set(dest_data)
    result: dict[str, list] = {"added": [], "removed": [], "changed": [], "unchanged": []}

    for key in sorted(all_keys):
        in_src = key in source_data
        in_dst = key in dest_data
        if in_src and not in_dst:
            result["added"].append(key)
        elif in_dst and not in_src:
            result["removed"].append(key)
        elif source_data[key] != dest_data[key]:
            result["changed"].append(key)
        else:
            result["unchanged"].append(key)

    return result
