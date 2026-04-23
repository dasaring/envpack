"""Replay module: re-apply a snapshot from history by index or label."""

from __future__ import annotations

import os
from typing import Optional

from envpack.history import list_history, find_by_label
from envpack.snapshot import load, save


class ReplayError(Exception):
    """Raised when a replay operation cannot be completed."""


def get_replay_target(history_file: str, index: Optional[int] = None, label: Optional[str] = None) -> dict:
    """Return the history entry to replay, identified by index or label.

    Raises ReplayError if not found.
    """
    if index is None and label is None:
        raise ReplayError("Must specify either index or label.")

    events = list_history(history_file)

    if label is not None:
        entry = find_by_label(history_file, label)
        if entry is None:
            raise ReplayError(f"No history entry with label {label!r}.")
        return entry

    if not events:
        raise ReplayError("History is empty; no entries to replay.")

    try:
        return events[index]
    except IndexError:
        raise ReplayError(f"History index {index} out of range (0\u2013{len(events) - 1}).")


def replay(history_file: str, dest: str, index: Optional[int] = None,
           label: Optional[str] = None, dry_run: bool = False) -> str:
    """Copy the snapshot referenced by a history entry to *dest*.

    Returns the resolved source path.
    Raises ReplayError if the source snapshot no longer exists.
    """
    entry = get_replay_target(history_file, index=index, label=label)
    source = entry["path"]

    if not os.path.isfile(source):
        raise ReplayError(f"Snapshot file not found: {source}")

    if not dry_run:
        snapshot = load(source)
        save(snapshot, dest)

    return source
