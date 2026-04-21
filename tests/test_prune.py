"""Tests for envpack.prune."""

import json
import os
import time
from pathlib import Path

import pytest

from envpack.prune import (
    find_old_snapshots,
    find_excess_snapshots,
    prune_snapshots,
    prune_summary,
)


def _write_snap(directory: Path, name: str, mtime_offset_days: float = 0) -> str:
    """Write a minimal snapshot JSON and optionally shift its mtime."""
    path = directory / name
    path.write_text(json.dumps({"KEY": "value"}))
    if mtime_offset_days:
        delta = mtime_offset_days * 86400
        new_time = time.time() - delta
        os.utime(str(path), (new_time, new_time))
    return str(path)


@pytest.fixture()
def snap_dir(tmp_path):
    return tmp_path


# --- find_old_snapshots ---

def test_find_old_snapshots_returns_old_files(snap_dir):
    old = _write_snap(snap_dir, "old.json", mtime_offset_days=10)
    _write_snap(snap_dir, "new.json", mtime_offset_days=1)
    result = find_old_snapshots(str(snap_dir), older_than_days=5)
    assert old in result


def test_find_old_snapshots_excludes_recent(snap_dir):
    _write_snap(snap_dir, "old.json", mtime_offset_days=10)
    new = _write_snap(snap_dir, "new.json", mtime_offset_days=1)
    result = find_old_snapshots(str(snap_dir), older_than_days=5)
    assert new not in result


def test_find_old_snapshots_empty_dir(snap_dir):
    assert find_old_snapshots(str(snap_dir), older_than_days=1) == []


# --- find_excess_snapshots ---

def test_find_excess_snapshots_keeps_newest(snap_dir):
    _write_snap(snap_dir, "a.json", mtime_offset_days=3)
    _write_snap(snap_dir, "b.json", mtime_offset_days=2)
    newest = _write_snap(snap_dir, "c.json", mtime_offset_days=0)
    excess = find_excess_snapshots(str(snap_dir), keep=1)
    assert newest not in excess
    assert len(excess) == 2


def test_find_excess_snapshots_none_when_under_limit(snap_dir):
    _write_snap(snap_dir, "a.json")
    assert find_excess_snapshots(str(snap_dir), keep=5) == []


def test_find_excess_snapshots_invalid_keep(snap_dir):
    with pytest.raises(ValueError):
        find_excess_snapshots(str(snap_dir), keep=0)


# --- prune_snapshots ---

def test_prune_removes_files(snap_dir):
    path = _write_snap(snap_dir, "old.json")
    removed = prune_snapshots([path])
    assert path in removed
    assert not os.path.exists(path)


def test_prune_dry_run_does_not_delete(snap_dir):
    path = _write_snap(snap_dir, "old.json")
    removed = prune_snapshots([path], dry_run=True)
    assert path in removed
    assert os.path.exists(path)


def test_prune_skips_pinned(snap_dir):
    path = _write_snap(snap_dir, "pinned.json")
    removed = prune_snapshots([path], pinned=[path])
    assert path not in removed
    assert os.path.exists(path)


# --- prune_summary ---

def test_prune_summary_nothing(snap_dir):
    assert prune_summary([]) == "Nothing to prune."


def test_prune_summary_lists_files(snap_dir):
    msg = prune_summary(["/tmp/a.json", "/tmp/b.json"])
    assert "Removed 2 snapshot(s)" in msg
    assert "/tmp/a.json" in msg


def test_prune_summary_dry_run_label(snap_dir):
    msg = prune_summary(["/tmp/a.json"], dry_run=True)
    assert "Would remove" in msg
