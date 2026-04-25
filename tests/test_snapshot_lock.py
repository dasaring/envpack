"""Tests for envpack.snapshot_lock."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from envpack.snapshot_lock import (
    lock_snapshot,
    unlock_snapshot,
    is_locked,
    list_locks,
)


@pytest.fixture()
def lock_file(tmp_path: Path) -> Path:
    return tmp_path / "locks.json"


def test_lock_new_snapshot_returns_true(lock_file):
    assert lock_snapshot("snap.json", lock_file=lock_file) is True


def test_lock_creates_file(lock_file):
    lock_snapshot("snap.json", lock_file=lock_file)
    assert lock_file.exists()


def test_lock_file_is_valid_json(lock_file):
    lock_snapshot("snap.json", reason="keep", lock_file=lock_file)
    data = json.loads(lock_file.read_text())
    assert isinstance(data, dict)


def test_lock_already_locked_returns_false(lock_file):
    lock_snapshot("snap.json", lock_file=lock_file)
    assert lock_snapshot("snap.json", lock_file=lock_file) is False


def test_lock_stores_reason(lock_file):
    lock_snapshot("snap.json", reason="production", lock_file=lock_file)
    data = json.loads(lock_file.read_text())
    assert data["snap.json"] == "production"


def test_is_locked_true_after_lock(lock_file):
    lock_snapshot("snap.json", lock_file=lock_file)
    assert is_locked("snap.json", lock_file=lock_file) is True


def test_is_locked_false_when_not_locked(lock_file):
    assert is_locked("snap.json", lock_file=lock_file) is False


def test_unlock_returns_true(lock_file):
    lock_snapshot("snap.json", lock_file=lock_file)
    assert unlock_snapshot("snap.json", lock_file=lock_file) is True


def test_unlock_removes_lock(lock_file):
    lock_snapshot("snap.json", lock_file=lock_file)
    unlock_snapshot("snap.json", lock_file=lock_file)
    assert is_locked("snap.json", lock_file=lock_file) is False


def test_unlock_missing_returns_false(lock_file):
    assert unlock_snapshot("snap.json", lock_file=lock_file) is False


def test_list_locks_empty(lock_file):
    assert list_locks(lock_file=lock_file) == []


def test_list_locks_returns_entries(lock_file):
    lock_snapshot("a.json", reason="r1", lock_file=lock_file)
    lock_snapshot("b.json", reason="r2", lock_file=lock_file)
    entries = list_locks(lock_file=lock_file)
    paths = {e["path"] for e in entries}
    assert paths == {"a.json", "b.json"}


def test_list_locks_entry_has_reason(lock_file):
    lock_snapshot("snap.json", reason="critical", lock_file=lock_file)
    entries = list_locks(lock_file=lock_file)
    assert entries[0]["reason"] == "critical"


def test_multiple_snapshots_independent(lock_file):
    lock_snapshot("a.json", lock_file=lock_file)
    unlock_snapshot("a.json", lock_file=lock_file)
    assert is_locked("a.json", lock_file=lock_file) is False
    assert is_locked("b.json", lock_file=lock_file) is False
