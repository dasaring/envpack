"""Tests for envpack.snapshot_flatten."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.snapshot_flatten import (
    FlattenError,
    flatten_groups,
    group_by_prefix,
    prefix_keys,
    save_groups,
    strip_prefix,
)


SNAP = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "envpack",
    "APP_ENV": "production",
    "PLAIN": "value",
}


def test_group_by_prefix_separates_correctly():
    groups = group_by_prefix(SNAP)
    assert set(groups["DB"]) == {"HOST", "PORT"}
    assert set(groups["APP"]) == {"NAME", "ENV"}
    assert groups["__root__"] == {"PLAIN": "value"}


def test_group_by_prefix_custom_sep():
    snap = {"DB.HOST": "h", "DB.PORT": "5432", "PLAIN": "v"}
    groups = group_by_prefix(snap, sep=".")
    assert "HOST" in groups["DB"]
    assert "__root__" in groups


def test_group_by_prefix_empty_snapshot():
    assert group_by_prefix({}) == {}


def test_flatten_groups_roundtrip():
    groups = group_by_prefix(SNAP)
    restored = flatten_groups(groups)
    assert restored == SNAP


def test_prefix_keys_adds_prefix():
    snap = {"HOST": "localhost", "PORT": "5432"}
    result = prefix_keys(snap, "DB")
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_prefix_keys_custom_sep():
    snap = {"HOST": "h"}
    result = prefix_keys(snap, "DB", sep=".")
    assert "DB.HOST" in result


def test_prefix_keys_empty_prefix_raises():
    with pytest.raises(FlattenError):
        prefix_keys({"K": "v"}, "")


def test_strip_prefix_removes_matching_keys():
    snap = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "x"}
    result = strip_prefix(snap, "DB")
    assert result == {"HOST": "localhost", "PORT": "5432"}


def test_strip_prefix_drops_non_matching():
    snap = {"DB_HOST": "h", "OTHER": "v"}
    result = strip_prefix(snap, "DB")
    assert "OTHER" not in result


def test_strip_prefix_empty_prefix_raises():
    with pytest.raises(FlattenError):
        strip_prefix({"K": "v"}, "")


def test_save_groups_creates_files(tmp_path):
    groups = {"DB": {"HOST": "h"}, "APP": {"NAME": "n"}}
    saved = save_groups(groups, tmp_path)
    assert len(saved) == 2
    names = {p.name for p in saved}
    assert "DB.json" in names
    assert "APP.json" in names


def test_save_groups_valid_json(tmp_path):
    groups = {"DB": {"HOST": "localhost"}}
    save_groups(groups, tmp_path)
    data = json.loads((tmp_path / "DB.json").read_text())
    assert data == {"HOST": "localhost"}


def test_save_groups_creates_output_dir(tmp_path):
    dest = tmp_path / "nested" / "output"
    save_groups({"X": {"K": "v"}}, dest)
    assert dest.is_dir()
