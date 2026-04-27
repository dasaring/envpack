"""Tests for envpack.snapshot_dedup."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.snapshot_dedup import (
    DedupGroup,
    _digest,
    dedup_summary,
    find_duplicates,
    find_duplicates_in_dir,
)


def _write(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture()
def snap_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_digest_is_deterministic() -> None:
    snap = {"A": "1", "B": "2"}
    assert _digest(snap) == _digest(snap)


def test_digest_differs_for_different_content() -> None:
    assert _digest({"A": "1"}) != _digest({"A": "2"})


def test_digest_order_independent() -> None:
    a = {"X": "1", "Y": "2"}
    b = {"Y": "2", "X": "1"}
    assert _digest(a) == _digest(b)


def test_find_duplicates_returns_empty_when_no_dupes(snap_dir: Path) -> None:
    _write(snap_dir / "a.json", {"K": "1"})
    _write(snap_dir / "b.json", {"K": "2"})
    groups = find_duplicates_in_dir(snap_dir)
    assert groups == []


def test_find_duplicates_detects_identical_files(snap_dir: Path) -> None:
    data = {"FOO": "bar", "BAZ": "qux"}
    _write(snap_dir / "snap1.json", data)
    _write(snap_dir / "snap2.json", data)
    groups = find_duplicates_in_dir(snap_dir)
    assert len(groups) == 1
    assert len(groups[0].paths) == 2


def test_find_duplicates_canonical_is_lexicographically_first(snap_dir: Path) -> None:
    data = {"ENV": "prod"}
    _write(snap_dir / "z_snap.json", data)
    _write(snap_dir / "a_snap.json", data)
    groups = find_duplicates_in_dir(snap_dir)
    assert groups[0].canonical().name == "a_snap.json"


def test_find_duplicates_duplicates_excludes_canonical(snap_dir: Path) -> None:
    data = {"ENV": "prod"}
    _write(snap_dir / "a.json", data)
    _write(snap_dir / "b.json", data)
    groups = find_duplicates_in_dir(snap_dir)
    dups = groups[0].duplicates()
    assert len(dups) == 1
    assert dups[0].name == "b.json"


def test_find_duplicates_skips_invalid_json(snap_dir: Path) -> None:
    (snap_dir / "bad.json").write_text("not-json", encoding="utf-8")
    _write(snap_dir / "good.json", {"K": "v"})
    groups = find_duplicates_in_dir(snap_dir)
    assert groups == []


def test_find_duplicates_not_a_directory(tmp_path: Path) -> None:
    fake = tmp_path / "not_a_dir"
    with pytest.raises(NotADirectoryError):
        find_duplicates_in_dir(fake)


def test_dedup_summary_no_groups() -> None:
    assert dedup_summary([]) == "No duplicates found."


def test_dedup_summary_contains_digest(snap_dir: Path) -> None:
    data = {"X": "y"}
    _write(snap_dir / "p.json", data)
    _write(snap_dir / "q.json", data)
    groups = find_duplicates_in_dir(snap_dir)
    summary = dedup_summary(groups)
    assert groups[0].digest[:12] in summary
    assert "p.json" in summary or "q.json" in summary


def test_dedup_group_is_duplicate_true() -> None:
    g = DedupGroup(digest="abc", paths=[Path("a"), Path("b")])
    assert g.is_duplicate() is True


def test_dedup_group_is_duplicate_false() -> None:
    g = DedupGroup(digest="abc", paths=[Path("a")])
    assert g.is_duplicate() is False
