"""Tests for envpack.namespace."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.namespace import (
    add_to_namespace,
    find_namespace_for_snapshot,
    get_snapshots_in_namespace,
    list_namespaces,
    remove_from_namespace,
)


@pytest.fixture()
def ns_file(tmp_path: Path) -> Path:
    return tmp_path / "namespaces.json"


def test_add_creates_namespace(ns_file: Path) -> None:
    result = add_to_namespace("prod", "snap_a.json", ns_file)
    assert result is True
    assert ns_file.exists()


def test_add_file_is_valid_json(ns_file: Path) -> None:
    add_to_namespace("prod", "snap_a.json", ns_file)
    data = json.loads(ns_file.read_text())
    assert isinstance(data, dict)


def test_add_no_duplicates(ns_file: Path) -> None:
    add_to_namespace("prod", "snap_a.json", ns_file)
    result = add_to_namespace("prod", "snap_a.json", ns_file)
    assert result is False
    snapshots = get_snapshots_in_namespace("prod", ns_file)
    assert snapshots.count("snap_a.json") == 1


def test_add_multiple_snapshots(ns_file: Path) -> None:
    add_to_namespace("prod", "snap_a.json", ns_file)
    add_to_namespace("prod", "snap_b.json", ns_file)
    snapshots = get_snapshots_in_namespace("prod", ns_file)
    assert "snap_a.json" in snapshots
    assert "snap_b.json" in snapshots


def test_remove_returns_true_when_found(ns_file: Path) -> None:
    add_to_namespace("staging", "snap_a.json", ns_file)
    result = remove_from_namespace("staging", "snap_a.json", ns_file)
    assert result is True


def test_remove_returns_false_when_absent(ns_file: Path) -> None:
    result = remove_from_namespace("staging", "snap_x.json", ns_file)
    assert result is False


def test_remove_empty_namespace_deleted(ns_file: Path) -> None:
    add_to_namespace("dev", "snap_a.json", ns_file)
    remove_from_namespace("dev", "snap_a.json", ns_file)
    assert "dev" not in list_namespaces(ns_file)


def test_list_namespaces_empty(ns_file: Path) -> None:
    assert list_namespaces(ns_file) == []


def test_list_namespaces_multiple(ns_file: Path) -> None:
    add_to_namespace("prod", "snap_a.json", ns_file)
    add_to_namespace("dev", "snap_b.json", ns_file)
    names = list_namespaces(ns_file)
    assert "prod" in names
    assert "dev" in names


def test_get_snapshots_unknown_namespace(ns_file: Path) -> None:
    assert get_snapshots_in_namespace("ghost", ns_file) == []


def test_find_namespace_for_snapshot(ns_file: Path) -> None:
    add_to_namespace("prod", "snap_a.json", ns_file)
    ns = find_namespace_for_snapshot("snap_a.json", ns_file)
    assert ns == "prod"


def test_find_namespace_returns_none_when_missing(ns_file: Path) -> None:
    ns = find_namespace_for_snapshot("ghost.json", ns_file)
    assert ns is None
