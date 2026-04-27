"""Tests for envpack.snapshot_diff_summary."""

import json
import pytest
from pathlib import Path

from envpack.snapshot_diff_summary import (
    diff_files,
    batch_diff,
    render_batch,
    FileDiffSummary,
)


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(directory: Path, name: str, data: dict) -> Path:
    p = directory / name
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_diff_files_identical(snap_dir):
    a = _write(snap_dir, "a.json", {"FOO": "1", "BAR": "2"})
    b = _write(snap_dir, "b.json", {"FOO": "1", "BAR": "2"})
    result = diff_files(a, b)
    assert result.is_identical is True
    assert result.added == []
    assert result.removed == []
    assert result.changed == []


def test_diff_files_detects_added(snap_dir):
    a = _write(snap_dir, "a.json", {"FOO": "1"})
    b = _write(snap_dir, "b.json", {"FOO": "1", "NEW_KEY": "hello"})
    result = diff_files(a, b)
    assert result.is_identical is False
    assert "NEW_KEY" in result.added
    assert result.removed == []
    assert result.changed == []


def test_diff_files_detects_removed(snap_dir):
    a = _write(snap_dir, "a.json", {"FOO": "1", "OLD": "bye"})
    b = _write(snap_dir, "b.json", {"FOO": "1"})
    result = diff_files(a, b)
    assert "OLD" in result.removed
    assert result.is_identical is False


def test_diff_files_detects_changed(snap_dir):
    a = _write(snap_dir, "a.json", {"FOO": "old"})
    b = _write(snap_dir, "b.json", {"FOO": "new"})
    result = diff_files(a, b)
    assert "FOO" in result.changed
    assert result.is_identical is False


def test_to_dict_keys(snap_dir):
    a = _write(snap_dir, "a.json", {"X": "1"})
    b = _write(snap_dir, "b.json", {"Y": "2"})
    d = diff_files(a, b).to_dict()
    assert set(d.keys()) == {"path_a", "path_b", "added", "removed", "changed", "is_identical"}


def test_render_identical(snap_dir):
    a = _write(snap_dir, "a.json", {"K": "v"})
    b = _write(snap_dir, "b.json", {"K": "v"})
    text = diff_files(a, b).render()
    assert "identical" in text


def test_render_shows_added_key(snap_dir):
    a = _write(snap_dir, "a.json", {})
    b = _write(snap_dir, "b.json", {"ADDED_KEY": "yes"})
    text = diff_files(a, b).render()
    assert "+ ADDED_KEY" in text


def test_batch_diff_returns_list(snap_dir):
    a = _write(snap_dir, "a.json", {"A": "1"})
    b = _write(snap_dir, "b.json", {"B": "2"})
    c = _write(snap_dir, "c.json", {"B": "2"})
    results = batch_diff([(a, b), (b, c)])
    assert len(results) == 2
    assert all(isinstance(r, FileDiffSummary) for r in results)


def test_render_batch_empty():
    assert render_batch([]) == "(no comparisons)"


def test_render_batch_multiple(snap_dir):
    a = _write(snap_dir, "a.json", {"X": "1"})
    b = _write(snap_dir, "b.json", {"X": "1"})
    c = _write(snap_dir, "c.json", {"X": "changed"})
    summaries = batch_diff([(a, b), (b, c)])
    report = render_batch(summaries)
    assert "identical" in report
    assert "~ X" in report
