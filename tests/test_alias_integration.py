"""Integration tests: alias round-trip with real snapshot files."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from envpack.alias import add_alias, list_aliases, remove_alias, resolve_alias
from envpack.snapshot import capture, save


@pytest.fixture()
def snapshot_path(tmp_path: Path) -> Path:
    env = {"APP_ENV": "production", "PORT": "8080"}
    snap = capture(list(env.keys()), env)
    path = tmp_path / "prod.json"
    save(snap, path)
    return path


@pytest.fixture()
def alias_file(tmp_path: Path) -> Path:
    return tmp_path / "aliases.json"


def test_alias_points_to_existing_snapshot(snapshot_path, alias_file):
    add_alias("prod", str(snapshot_path), alias_file)
    resolved = resolve_alias("prod", alias_file)
    assert Path(resolved).exists()


def test_alias_lifecycle(snapshot_path, alias_file):
    add_alias("prod", str(snapshot_path), alias_file)
    assert resolve_alias("prod", alias_file) == str(snapshot_path)

    add_alias("prod", "/other/path.json", alias_file)
    assert resolve_alias("prod", alias_file) == "/other/path.json"

    remove_alias("prod", alias_file)
    assert resolve_alias("prod", alias_file) is None


def test_multiple_aliases_independent(snapshot_path, alias_file):
    add_alias("a", str(snapshot_path), alias_file)
    add_alias("b", "/snaps/b.json", alias_file)
    add_alias("c", "/snaps/c.json", alias_file)

    remove_alias("b", alias_file)

    remaining = list_aliases(alias_file)
    assert "a" in remaining
    assert "b" not in remaining
    assert "c" in remaining


def test_list_aliases_reflects_all_additions(alias_file):
    names = ["alpha", "beta", "gamma"]
    for name in names:
        add_alias(name, f"/snaps/{name}.json", alias_file)

    result = list_aliases(alias_file)
    assert set(result.keys()) == set(names)
