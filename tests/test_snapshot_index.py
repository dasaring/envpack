"""Tests for envpack.snapshot_index."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from envpack.snapshot_index import (
    IndexEntry,
    build_index,
    find_by_key,
    largest,
    summary,
)


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    """Directory with three pre-written snapshot files."""
    snaps = [
        {"env": {"HOME": "/home/alice", "PATH": "/usr/bin"}, "captured_at": "2024-01-01T00:00:00"},
        {"env": {"DATABASE_URL": "postgres://localhost/db"}, "captured_at": "2024-02-01T00:00:00"},
        {"env": {"HOME": "/home/bob", "SECRET_KEY": "abc", "PORT": "8080"}, "captured_at": None},
    ]
    for i, snap in enumerate(snaps):
        (tmp_path / f"snap_{i}.json").write_text(json.dumps(snap), encoding="utf-8")
    return tmp_path


def test_build_index_returns_entries(snap_dir):
    index = build_index(str(snap_dir))
    assert len(index) == 3


def test_build_index_entry_fields(snap_dir):
    index = build_index(str(snap_dir))
    entry = index[0]  # snap_0.json
    assert entry.key_count == 2
    assert entry.captured_at == "2024-01-01T00:00:00"
    assert entry.size_bytes > 0
    assert entry.path.endswith(".json")


def test_build_index_not_a_directory(tmp_path):
    fake = str(tmp_path / "nonexistent")
    with pytest.raises(NotADirectoryError):
        build_index(fake)


def test_build_index_skips_invalid_json(tmp_path):
    (tmp_path / "bad.json").write_text("not json", encoding="utf-8")
    (tmp_path / "good.json").write_text(json.dumps({"env": {"A": "1"}}), encoding="utf-8")
    index = build_index(str(tmp_path))
    assert len(index) == 1


def test_build_index_empty_dir(tmp_path):
    index = build_index(str(tmp_path))
    assert index == []


def test_find_by_key_returns_matches(snap_dir):
    index = build_index(str(snap_dir))
    matches = find_by_key(index, "HOME")
    assert len(matches) == 2


def test_find_by_key_no_match(snap_dir):
    index = build_index(str(snap_dir))
    matches = find_by_key(index, "NONEXISTENT_KEY")
    assert matches == []


def test_largest_returns_sorted(snap_dir):
    index = build_index(str(snap_dir))
    top = largest(index, n=2)
    assert len(top) == 2
    assert top[0].key_count >= top[1].key_count


def test_largest_n_exceeds_index(snap_dir):
    index = build_index(str(snap_dir))
    top = largest(index, n=100)
    assert len(top) == 3


def test_summary_string(snap_dir):
    index = build_index(str(snap_dir))
    s = summary(index)
    assert "3 snapshot(s)" in s
    assert "total keys" in s
    assert "bytes" in s


def test_entry_to_dict():
    entry = IndexEntry(path="/tmp/a.json", captured_at="2024-01-01", key_count=3, size_bytes=128)
    d = entry.to_dict()
    assert d["path"] == "/tmp/a.json"
    assert d["key_count"] == 3
