"""Tests for envpack.snapshot_tag_filter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.snapshot_tag_filter import (
    filter_snapshots,
    snapshots_with_any_tag,
    snapshots_with_all_tags,
    snapshots_excluding_tags,
)


@pytest.fixture()
def tags_file(tmp_path: Path) -> Path:
    data = {
        "prod": ["/snaps/a.json", "/snaps/b.json"],
        "staging": ["/snaps/b.json", "/snaps/c.json"],
        "db": ["/snaps/a.json", "/snaps/c.json"],
    }
    f = tmp_path / "tags.json"
    f.write_text(json.dumps(data))
    return f


def test_any_tag_returns_union(tags_file: Path) -> None:
    result = snapshots_with_any_tag(["prod", "staging"], tags_file=tags_file)
    assert set(result) == {"/snaps/a.json", "/snaps/b.json", "/snaps/c.json"}


def test_any_tag_single(tags_file: Path) -> None:
    result = snapshots_with_any_tag(["db"], tags_file=tags_file)
    assert set(result) == {"/snaps/a.json", "/snaps/c.json"}


def test_any_tag_empty_list(tags_file: Path) -> None:
    assert snapshots_with_any_tag([], tags_file=tags_file) == []


def test_all_tags_returns_intersection(tags_file: Path) -> None:
    result = snapshots_with_all_tags(["prod", "db"], tags_file=tags_file)
    assert result == ["/snaps/a.json"]


def test_all_tags_no_common(tags_file: Path) -> None:
    result = snapshots_with_all_tags(["prod", "staging", "db"], tags_file=tags_file)
    assert result == []


def test_all_tags_single(tags_file: Path) -> None:
    result = snapshots_with_all_tags(["staging"], tags_file=tags_file)
    assert set(result) == {"/snaps/b.json", "/snaps/c.json"}


def test_all_tags_empty_list(tags_file: Path) -> None:
    assert snapshots_with_all_tags([], tags_file=tags_file) == []


def test_excluding_tags_removes_tagged(tags_file: Path) -> None:
    result = snapshots_excluding_tags(["prod"], tags_file=tags_file)
    assert "/snaps/a.json" not in result
    assert "/snaps/b.json" not in result
    assert "/snaps/c.json" in result


def test_excluding_all_tags_returns_empty(tags_file: Path) -> None:
    result = snapshots_excluding_tags(["prod", "staging", "db"], tags_file=tags_file)
    assert result == []


def test_filter_snapshots_any(tags_file: Path) -> None:
    result = filter_snapshots(any_tags=["staging"], tags_file=tags_file)
    assert set(result) == {"/snaps/b.json", "/snaps/c.json"}


def test_filter_snapshots_all_and_exclude(tags_file: Path) -> None:
    # all=[prod, db] -> [a], exclude=[staging] -> a is not staging, so [a] remains
    result = filter_snapshots(all_tags=["prod", "db"], exclude_tags=["staging"], tags_file=tags_file)
    assert result == ["/snaps/a.json"]


def test_filter_snapshots_exclude_only(tags_file: Path) -> None:
    result = filter_snapshots(exclude_tags=["db"], tags_file=tags_file)
    assert "/snaps/a.json" not in result
    assert "/snaps/c.json" not in result
    assert "/snaps/b.json" in result


def test_filter_snapshots_no_criteria_returns_all(tags_file: Path) -> None:
    result = filter_snapshots(tags_file=tags_file)
    assert set(result) == {"/snaps/a.json", "/snaps/b.json", "/snaps/c.json"}
