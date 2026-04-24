"""Retention policy management for envpack snapshots."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_DEFAULT_POLICY_FILE = Path(".envpack_retention.json")


def _load_policy(policy_file: Path) -> dict:
    if policy_file.exists():
        with policy_file.open() as f:
            return json.load(f)
    return {}


def _save_policy(policy: dict, policy_file: Path) -> None:
    with policy_file.open("w") as f:
        json.dump(policy, f, indent=2)


def set_policy(
    name: str,
    max_count: int | None = None,
    max_age_days: int | None = None,
    policy_file: Path = _DEFAULT_POLICY_FILE,
) -> dict[str, Any]:
    """Create or update a named retention policy."""
    if max_count is None and max_age_days is None:
        raise ValueError("At least one of max_count or max_age_days must be set.")
    policy = _load_policy(policy_file)
    entry: dict[str, Any] = {"name": name}
    if max_count is not None:
        entry["max_count"] = max_count
    if max_age_days is not None:
        entry["max_age_days"] = max_age_days
    policy[name] = entry
    _save_policy(policy, policy_file)
    return entry


def get_policy(
    name: str, policy_file: Path = _DEFAULT_POLICY_FILE
) -> dict[str, Any] | None:
    """Retrieve a named retention policy, or None if not found."""
    return _load_policy(policy_file).get(name)


def remove_policy(
    name: str, policy_file: Path = _DEFAULT_POLICY_FILE
) -> bool:
    """Remove a named retention policy. Returns True if removed, False if not found."""
    policy = _load_policy(policy_file)
    if name not in policy:
        return False
    del policy[name]
    _save_policy(policy, policy_file)
    return True


def list_policies(
    policy_file: Path = _DEFAULT_POLICY_FILE,
) -> list[dict[str, Any]]:
    """Return all defined retention policies."""
    return list(_load_policy(policy_file).values())


def apply_policy(
    name: str,
    snapshot_paths: list[Path],
    policy_file: Path = _DEFAULT_POLICY_FILE,
) -> list[Path]:
    """Return the list of snapshot paths that should be pruned under the named policy.

    Snapshots are assumed to be ordered oldest-first.
    """
    entry = get_policy(name, policy_file)
    if entry is None:
        raise KeyError(f"Retention policy '{name}' not found.")

    to_prune: list[Path] = []

    if "max_age_days" in entry:
        import time
        max_age_seconds = entry["max_age_days"] * 86400
        now = time.time()
        for p in snapshot_paths:
            if p.exists() and (now - p.stat().st_mtime) > max_age_seconds:
                to_prune.append(p)

    if "max_count" in entry:
        remaining = [p for p in snapshot_paths if p not in to_prune]
        excess = len(remaining) - entry["max_count"]
        if excess > 0:
            to_prune.extend(remaining[:excess])

    return to_prune
