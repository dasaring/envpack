"""Watch for environment variable changes between two points in time."""

from __future__ import annotations

import os
import time
from typing import Callable, Optional

from envpack.snapshot import capture
from envpack.diff import compute_diff, DiffResult


def poll_for_changes(
    interval: float = 1.0,
    keys: Optional[list] = None,
    callback: Optional[Callable[[DiffResult], None]] = None,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll environment variables at *interval* seconds and invoke *callback* on changes.

    Parameters
    ----------
    interval:       seconds between polls
    keys:           restrict monitoring to these keys (None = all)
    callback:       called with a DiffResult whenever a change is detected
    max_iterations: stop after this many iterations (useful for testing)
    """
    previous = capture(keys=keys)
    iterations = 0

    while True:
        time.sleep(interval)
        current = capture(keys=keys)
        diff = compute_diff(previous, current)

        if not diff.is_empty():
            if callback:
                callback(diff)
            previous = current

        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break


def snapshot_diff_from_baseline(baseline: dict, keys: Optional[list] = None) -> DiffResult:
    """Return a diff between *baseline* snapshot and the current environment."""
    current = capture(keys=keys)
    return compute_diff(baseline, current)


def changed_since(baseline: dict, keys: Optional[list] = None) -> list[str]:
    """Return list of keys that changed since *baseline* was captured."""
    diff = snapshot_diff_from_baseline(baseline, keys=keys)
    return list(diff.added) + list(diff.removed) + list(diff.changed)
