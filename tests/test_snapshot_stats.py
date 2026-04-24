"""Tests for envpack.snapshot_stats."""

from __future__ import annotations

import json
import os

import pytest

from envpack.snapshot_stats import compute_stats, stats_from_directory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_snap(path: str, data: dict) -> str:
    with open(path, "w") as fh:
        json.dump(data, fh)
    return path


@pytest.fixture()
def snap_dir(tmp_path):
    return tmp_path


# ---------------------------------------------------------------------------
# compute_stats
# ---------------------------------------------------------------------------

def test_compute_stats_empty_list_returns_none():
    assert compute_stats([]) is None


def test_compute_stats_single_snapshot(snap_dir):
    p = _write_snap(str(snap_dir / "a.json"), {"A": "1", "B": "2"})
    result = compute_stats([p])
    assert result is not None
    assert result.count == 1
    assert result.total_keys == 2
    assert result.avg_keys == 2.0
    assert result.min_keys == 2
    assert result.max_keys == 2


def test_compute_stats_multiple_snapshots(snap_dir):
    p1 = _write_snap(str(snap_dir / "a.json"), {"A": "1", "B": "2"})
    p2 = _write_snap(str(snap_dir / "b.json"), {"A": "3", "C": "4"})
    result = compute_stats([p1, p2])
    assert result is not None
    assert result.count == 2
    assert result.total_keys == 4
    assert result.avg_keys == 2.0


def test_compute_stats_common_keys(snap_dir):
    p1 = _write_snap(str(snap_dir / "a.json"), {"SHARED": "x", "ONLY_A": "y"})
    p2 = _write_snap(str(snap_dir / "b.json"), {"SHARED": "z", "ONLY_B": "w"})
    result = compute_stats([p1, p2])
    assert result is not None
    assert "SHARED" in result.common_keys
    assert "ONLY_A" not in result.common_keys
    assert "ONLY_B" not in result.common_keys


def test_compute_stats_unique_keys(snap_dir):
    p1 = _write_snap(str(snap_dir / "a.json"), {"SHARED": "x", "SOLO": "1"})
    p2 = _write_snap(str(snap_dir / "b.json"), {"SHARED": "z"})
    result = compute_stats([p1, p2])
    assert result is not None
    assert "SOLO" in result.unique_keys
    assert "SHARED" not in result.unique_keys


def test_compute_stats_key_frequency(snap_dir):
    p1 = _write_snap(str(snap_dir / "a.json"), {"K": "1"})
    p2 = _write_snap(str(snap_dir / "b.json"), {"K": "2"})
    p3 = _write_snap(str(snap_dir / "c.json"), {"K": "3", "X": "4"})
    result = compute_stats([p1, p2, p3])
    assert result is not None
    assert result.key_frequency["K"] == 3
    assert result.key_frequency["X"] == 1


def test_compute_stats_skips_invalid_file(snap_dir):
    bad = str(snap_dir / "bad.json")
    with open(bad, "w") as fh:
        fh.write("not json")
    good = _write_snap(str(snap_dir / "good.json"), {"A": "1"})
    result = compute_stats([bad, good])
    assert result is not None
    assert result.count == 1


# ---------------------------------------------------------------------------
# stats_from_directory
# ---------------------------------------------------------------------------

def test_stats_from_directory_not_a_directory(tmp_path):
    with pytest.raises(NotADirectoryError):
        stats_from_directory(str(tmp_path / "nonexistent"))


def test_stats_from_directory_empty_dir(tmp_path):
    assert stats_from_directory(str(tmp_path)) is None


def test_stats_from_directory_reads_json_files(snap_dir):
    _write_snap(str(snap_dir / "a.json"), {"X": "1"})
    _write_snap(str(snap_dir / "b.json"), {"X": "2", "Y": "3"})
    # non-json file should be ignored
    (snap_dir / "notes.txt").write_text("ignore me")
    result = stats_from_directory(str(snap_dir))
    assert result is not None
    assert result.count == 2


def test_summary_contains_expected_fields(snap_dir):
    p = _write_snap(str(snap_dir / "a.json"), {"A": "1"})
    result = compute_stats([p])
    assert result is not None
    s = result.summary()
    assert "Snapshots analysed" in s
    assert "Avg keys" in s
