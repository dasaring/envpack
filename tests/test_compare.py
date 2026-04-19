"""Tests for envpack.compare module."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from envpack.compare import compare_files, compare_to_current, compare_summary, report
from envpack.diff import is_empty


@pytest.fixture()
def snap_a(tmp_path: Path) -> Path:
    p = tmp_path / "a.json"
    p.write_text(json.dumps({"FOO": "1", "BAR": "hello", "OLD": "gone"}))
    return p


@pytest.fixture()
def snap_b(tmp_path: Path) -> Path:
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"FOO": "2", "BAR": "hello", "NEW": "here"}))
    return p


def test_compare_files_detects_changes(snap_a: Path, snap_b: Path) -> None:
    result = compare_files(snap_a, snap_b)
    assert "FOO" in result["changed"]
    assert "OLD" in result["removed"]
    assert "NEW" in result["added"]
    assert "BAR" not in result["changed"]


def test_compare_files_identical(tmp_path: Path) -> None:
    data = json.dumps({"X": "1"})
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(data)
    b.write_text(data)
    result = compare_files(a, b)
    assert is_empty(result)


def test_compare_summary_returns_string(snap_a: Path, snap_b: Path) -> None:
    s = compare_summary(snap_a, snap_b)
    assert isinstance(s, str)
    assert len(s) > 0


def test_compare_to_current_uses_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MYVAR", "live_value")
    snap = tmp_path / "snap.json"
    snap.write_text(json.dumps({"MYVAR": "old_value"}))
    result = compare_to_current(snap)
    assert "MYVAR" in result["changed"]


def test_compare_to_current_no_diff(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STABLEVAR", "same")
    snap = tmp_path / "snap.json"
    snap.write_text(json.dumps({"STABLEVAR": "same"}))
    result = compare_to_current(snap)
    assert is_empty(result)


def test_report_verbose_shows_values(snap_a: Path, snap_b: Path) -> None:
    result = compare_files(snap_a, snap_b)
    out = report(result, verbose=True)
    assert "1" in out or "2" in out


def test_report_non_verbose_hides_values(snap_a: Path, snap_b: Path) -> None:
    result = compare_files(snap_a, snap_b)
    out = report(result, verbose=False)
    assert "***" in out


def test_report_no_diff(tmp_path: Path) -> None:
    result = {"added": {}, "removed": {}, "changed": {}}
    out = report(result)  # type: ignore[arg-type]
    assert "No differences" in out
