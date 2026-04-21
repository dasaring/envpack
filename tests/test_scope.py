"""Tests for envpack.scope."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from envpack.scope import (
    add_to_scope,
    remove_from_scope,
    list_scopes,
    get_snapshots_in_scope,
    find_scope_for_snapshot,
)


@pytest.fixture
def scope_file(tmp_path: Path) -> Path:
    return tmp_path / "scopes.json"


def test_add_creates_scope(scope_file):
    add_to_scope("prod", "snap_a.json", scope_file)
    assert "prod" in list_scopes(scope_file)


def test_add_returns_true_for_new(scope_file):
    result = add_to_scope("dev", "snap_a.json", scope_file)
    assert result is True


def test_add_returns_false_for_duplicate(scope_file):
    add_to_scope("dev", "snap_a.json", scope_file)
    result = add_to_scope("dev", "snap_a.json", scope_file)
    assert result is False


def test_add_no_duplicates(scope_file):
    add_to_scope("dev", "snap_a.json", scope_file)
    add_to_scope("dev", "snap_a.json", scope_file)
    snaps = get_snapshots_in_scope("dev", scope_file)
    assert snaps.count("snap_a.json") == 1


def test_add_multiple_snapshots(scope_file):
    add_to_scope("dev", "snap_a.json", scope_file)
    add_to_scope("dev", "snap_b.json", scope_file)
    snaps = get_snapshots_in_scope("dev", scope_file)
    assert "snap_a.json" in snaps
    assert "snap_b.json" in snaps


def test_scope_file_is_valid_json(scope_file):
    add_to_scope("prod", "snap_a.json", scope_file)
    data = json.loads(scope_file.read_text())
    assert isinstance(data, dict)


def test_remove_returns_true(scope_file):
    add_to_scope("prod", "snap_a.json", scope_file)
    result = remove_from_scope("prod", "snap_a.json", scope_file)
    assert result is True


def test_remove_returns_false_when_absent(scope_file):
    result = remove_from_scope("prod", "snap_x.json", scope_file)
    assert result is False


def test_remove_cleans_empty_scope(scope_file):
    add_to_scope("prod", "snap_a.json", scope_file)
    remove_from_scope("prod", "snap_a.json", scope_file)
    assert "prod" not in list_scopes(scope_file)


def test_list_scopes_empty(scope_file):
    assert list_scopes(scope_file) == []


def test_list_scopes_multiple(scope_file):
    add_to_scope("dev", "a.json", scope_file)
    add_to_scope("prod", "b.json", scope_file)
    scopes = list_scopes(scope_file)
    assert set(scopes) == {"dev", "prod"}


def test_get_snapshots_unknown_scope(scope_file):
    assert get_snapshots_in_scope("unknown", scope_file) == []


def test_find_scope_for_snapshot(scope_file):
    add_to_scope("staging", "snap_s.json", scope_file)
    found = find_scope_for_snapshot("snap_s.json", scope_file)
    assert found == "staging"


def test_find_scope_returns_none_when_missing(scope_file):
    result = find_scope_for_snapshot("ghost.json", scope_file)
    assert result is None
