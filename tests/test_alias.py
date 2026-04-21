"""Tests for envpack.alias."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.alias import (
    add_alias,
    list_aliases,
    remove_alias,
    resolve_alias,
)


@pytest.fixture()
def alias_file(tmp_path: Path) -> Path:
    return tmp_path / "aliases.json"


def test_add_alias_returns_true_for_new(alias_file):
    assert add_alias("prod", "/snaps/prod.json", alias_file) is True


def test_add_alias_creates_file(alias_file):
    add_alias("prod", "/snaps/prod.json", alias_file)
    assert alias_file.exists()


def test_add_alias_file_is_valid_json(alias_file):
    add_alias("prod", "/snaps/prod.json", alias_file)
    data = json.loads(alias_file.read_text())
    assert isinstance(data, dict)


def test_add_alias_returns_false_when_updated(alias_file):
    add_alias("prod", "/snaps/prod.json", alias_file)
    result = add_alias("prod", "/snaps/prod_v2.json", alias_file)
    assert result is False


def test_add_alias_overwrites_path(alias_file):
    add_alias("prod", "/snaps/prod.json", alias_file)
    add_alias("prod", "/snaps/prod_v2.json", alias_file)
    assert resolve_alias("prod", alias_file) == "/snaps/prod_v2.json"


def test_resolve_alias_returns_path(alias_file):
    add_alias("staging", "/snaps/staging.json", alias_file)
    assert resolve_alias("staging", alias_file) == "/snaps/staging.json"


def test_resolve_alias_missing_returns_none(alias_file):
    assert resolve_alias("nonexistent", alias_file) is None


def test_remove_alias_returns_true(alias_file):
    add_alias("dev", "/snaps/dev.json", alias_file)
    assert remove_alias("dev", alias_file) is True


def test_remove_alias_deletes_entry(alias_file):
    add_alias("dev", "/snaps/dev.json", alias_file)
    remove_alias("dev", alias_file)
    assert resolve_alias("dev", alias_file) is None


def test_remove_alias_missing_returns_false(alias_file):
    assert remove_alias("ghost", alias_file) is False


def test_list_aliases_empty(alias_file):
    assert list_aliases(alias_file) == {}


def test_list_aliases_multiple(alias_file):
    add_alias("prod", "/snaps/prod.json", alias_file)
    add_alias("dev", "/snaps/dev.json", alias_file)
    result = list_aliases(alias_file)
    assert result == {"prod": "/snaps/prod.json", "dev": "/snaps/dev.json"}
