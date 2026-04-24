"""Tests for envpack.snapshot_search."""

from __future__ import annotations

import json
import os

import pytest

from envpack.snapshot_search import (
    SearchResult,
    search_by_key,
    search_by_value,
    search_snapshots,
)


@pytest.fixture()
def snap_dir(tmp_path):
    snaps = [
        ("a.json", {"vars": {"DATABASE_URL": "postgres://localhost", "PORT": "5432"}}),
        ("b.json", {"vars": {"API_KEY": "secret123", "PORT": "8080"}}),
        ("c.json", {"vars": {"DATABASE_URL": "mysql://host", "DEBUG": "true"}}),
    ]
    for fname, data in snaps:
        (tmp_path / fname).write_text(json.dumps(data))
    return tmp_path


def test_search_by_key_exact(snap_dir):
    results = search_by_key(str(snap_dir), "PORT")
    paths = [os.path.basename(r.path) for r in results]
    assert "a.json" in paths
    assert "b.json" in paths
    assert "c.json" not in paths


def test_search_by_key_glob(snap_dir):
    results = search_by_key(str(snap_dir), "DATABASE_*")
    paths = [os.path.basename(r.path) for r in results]
    assert "a.json" in paths
    assert "c.json" in paths
    assert "b.json" not in paths


def test_search_by_key_no_match(snap_dir):
    results = search_by_key(str(snap_dir), "NONEXISTENT")
    assert results == []


def test_search_by_value_glob(snap_dir):
    results = search_by_value(str(snap_dir), "*postgres*")
    paths = [os.path.basename(r.path) for r in results]
    assert "a.json" in paths
    assert "b.json" not in paths


def test_search_by_value_no_match(snap_dir):
    results = search_by_value(str(snap_dir), "*NOPE*")
    assert results == []


def test_search_snapshots_key_only(snap_dir):
    results = search_snapshots(str(snap_dir), key_pattern="API_KEY")
    assert len(results) == 1
    assert os.path.basename(results[0].path) == "b.json"


def test_search_snapshots_value_only(snap_dir):
    results = search_snapshots(str(snap_dir), value_pattern="true")
    paths = [os.path.basename(r.path) for r in results]
    assert "c.json" in paths


def test_search_snapshots_both_patterns(snap_dir):
    results = search_snapshots(str(snap_dir), key_pattern="DATABASE_URL", value_pattern="*mysql*")
    assert len(results) == 1
    assert os.path.basename(results[0].path) == "c.json"


def test_search_snapshots_no_criteria_raises(snap_dir):
    with pytest.raises(ValueError, match="At least one"):
        search_snapshots(str(snap_dir))


def test_search_result_to_dict():
    r = SearchResult(path="/tmp/x.json", matched_keys=["FOO", "BAR"])
    d = r.to_dict()
    assert d["path"] == "/tmp/x.json"
    assert d["matched_keys"] == ["FOO", "BAR"]


def test_search_skips_invalid_json(tmp_path):
    (tmp_path / "bad.json").write_text("not json")
    results = search_by_key(str(tmp_path), "*")
    assert results == []
