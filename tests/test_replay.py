"""Tests for envpack.replay."""

from __future__ import annotations

import json
import os
import pytest

from envpack.replay import get_replay_target, replay, ReplayError


@pytest.fixture()
def history_file(tmp_path):
    return str(tmp_path / "history.json")


@pytest.fixture()
def snap_a(tmp_path):
    p = tmp_path / "snap_a.json"
    p.write_text(json.dumps({"FOO": "bar", "BAZ": "qux"}))
    return str(p)


@pytest.fixture()
def snap_b(tmp_path):
    p = tmp_path / "snap_b.json"
    p.write_text(json.dumps({"HELLO": "world"}))
    return str(p)


def _write_history(history_file, entries):
    with open(history_file, "w") as fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")


def test_get_replay_target_by_index(history_file, snap_a, snap_b):
    _write_history(history_file, [
        {"path": snap_a, "label": "first", "timestamp": "2024-01-01T00:00:00"},
        {"path": snap_b, "label": "second", "timestamp": "2024-01-02T00:00:00"},
    ])
    entry = get_replay_target(history_file, index=0)
    assert entry["path"] == snap_a


def test_get_replay_target_by_label(history_file, snap_a, snap_b):
    _write_history(history_file, [
        {"path": snap_a, "label": "alpha", "timestamp": "2024-01-01T00:00:00"},
        {"path": snap_b, "label": "beta", "timestamp": "2024-01-02T00:00:00"},
    ])
    entry = get_replay_target(history_file, label="beta")
    assert entry["path"] == snap_b


def test_get_replay_target_bad_index_raises(history_file, snap_a):
    _write_history(history_file, [
        {"path": snap_a, "label": "only", "timestamp": "2024-01-01T00:00:00"},
    ])
    with pytest.raises(ReplayError):
        get_replay_target(history_file, index=99)


def test_get_replay_target_bad_label_raises(history_file, snap_a):
    _write_history(history_file, [
        {"path": snap_a, "label": "only", "timestamp": "2024-01-01T00:00:00"},
    ])
    with pytest.raises(ReplayError):
        get_replay_target(history_file, label="nonexistent")


def test_get_replay_target_no_selector_raises(history_file):
    with pytest.raises(ReplayError):
        get_replay_target(history_file)


def test_replay_writes_dest(tmp_path, history_file, snap_a):
    _write_history(history_file, [
        {"path": snap_a, "label": "v1", "timestamp": "2024-01-01T00:00:00"},
    ])
    dest = str(tmp_path / "out.json")
    source = replay(history_file, dest, index=0)
    assert source == snap_a
    assert os.path.isfile(dest)
    data = json.loads(open(dest).read())
    assert data["FOO"] == "bar"


def test_replay_dry_run_does_not_write(tmp_path, history_file, snap_a):
    _write_history(history_file, [
        {"path": snap_a, "label": "v1", "timestamp": "2024-01-01T00:00:00"},
    ])
    dest = str(tmp_path / "out.json")
    replay(history_file, dest, index=0, dry_run=True)
    assert not os.path.isfile(dest)


def test_replay_missing_snapshot_raises(tmp_path, history_file):
    _write_history(history_file, [
        {"path": "/nonexistent/snap.json", "label": "ghost", "timestamp": "2024-01-01T00:00:00"},
    ])
    dest = str(tmp_path / "out.json")
    with pytest.raises(ReplayError, match="not found"):
        replay(history_file, dest, index=0)
