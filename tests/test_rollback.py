"""Tests for envpack.rollback."""

import json
import os
from pathlib import Path

import pytest

from envpack.rollback import get_rollback_target, rollback, RollbackError
from envpack.snapshot import save


@pytest.fixture()
def history_file(tmp_path):
    hf = tmp_path / "history.json"
    entries = [
        {"path": str(tmp_path / "snap_a.json"), "label": "v1", "timestamp": "2024-01-01T00:00:00"},
        {"path": str(tmp_path / "snap_b.json"), "label": "v2", "timestamp": "2024-01-02T00:00:00"},
    ]
    with hf.open("w") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")
    return hf


@pytest.fixture()
def snap_a(tmp_path):
    path = tmp_path / "snap_a.json"
    save({"FOO": "1", "BAR": "old"}, str(path))
    return path


@pytest.fixture()
def snap_b(tmp_path):
    path = tmp_path / "snap_b.json"
    save({"FOO": "2", "BAZ": "new"}, str(path))
    return path


def test_get_rollback_target_by_index(history_file):
    entry = get_rollback_target(history_file, index=-1)
    assert entry["label"] == "v2"


def test_get_rollback_target_by_label(history_file):
    entry = get_rollback_target(history_file, label="v1")
    assert entry["label"] == "v1"


def test_get_rollback_target_missing_label(history_file):
    with pytest.raises(RollbackError, match="No history entry"):
        get_rollback_target(history_file, label="nonexistent")


def test_get_rollback_target_empty_history(tmp_path):
    empty = tmp_path / "empty.json"
    empty.write_text("")
    with pytest.raises(RollbackError, match="History is empty"):
        get_rollback_target(empty)


def test_rollback_writes_file(tmp_path, snap_a):
    dest = str(tmp_path / "current.json")
    result = rollback(str(snap_a), dest)
    assert os.path.exists(dest)
    assert result["dry_run"] is False


def test_rollback_dry_run_does_not_write(tmp_path, snap_a):
    dest = str(tmp_path / "current.json")
    rollback(str(snap_a), dest, dry_run=True)
    assert not os.path.exists(dest)


def test_rollback_diff_reflects_changes(tmp_path, snap_a, snap_b):
    dest = str(tmp_path / "current.json")
    # Establish current state
    rollback(str(snap_a), dest)
    # Roll back to snap_b (which has different vars)
    result = rollback(str(snap_b), dest)
    diff = result["diff"]
    assert "BAZ" in diff.added
    assert "BAR" in diff.removed


def test_rollback_no_diff_when_identical(tmp_path, snap_a):
    dest = str(tmp_path / "current.json")
    rollback(str(snap_a), dest)
    result = rollback(str(snap_a), dest)
    from envpack.diff import is_empty
    assert is_empty(result["diff"])
