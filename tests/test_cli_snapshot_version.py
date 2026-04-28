"""Tests for envpack.cli_snapshot_version."""

import sys
import pytest
from pathlib import Path
from types import SimpleNamespace

from envpack.cli_snapshot_version import (
    cmd_version_add,
    cmd_version_list,
    cmd_version_get,
    cmd_version_delete,
    cmd_version_names,
)
from envpack.snapshot_version import add_version


@pytest.fixture
def store(tmp_path):
    return tmp_path / "versions.json"


def make_args(**kwargs):
    defaults = {"store": ".envpack_versions.json", "label": None, "index": -1}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_add_prints_snapshot(store, capsys):
    args = make_args(name="prod", snapshot="/snaps/prod.json", store=str(store))
    cmd_version_add(args)
    out = capsys.readouterr().out
    assert "/snaps/prod.json" in out
    assert "prod" in out


def test_cmd_add_prints_label(store, capsys):
    args = make_args(name="prod", snapshot="/snaps/prod.json", label="v1", store=str(store))
    cmd_version_add(args)
    out = capsys.readouterr().out
    assert "v1" in out


def test_cmd_list_shows_versions(store, capsys):
    add_version("prod", "/snaps/v1.json", store=store)
    add_version("prod", "/snaps/v2.json", store=store)
    args = make_args(name="prod", store=str(store))
    cmd_version_list(args)
    out = capsys.readouterr().out
    assert "/snaps/v1.json" in out
    assert "/snaps/v2.json" in out


def test_cmd_list_empty_prints_message(store, capsys):
    args = make_args(name="ghost", store=str(store))
    cmd_version_list(args)
    out = capsys.readouterr().out
    assert "No versions" in out


def test_cmd_get_prints_latest(store, capsys):
    add_version("prod", "/snaps/v1.json", store=store)
    add_version("prod", "/snaps/v2.json", store=store)
    args = make_args(name="prod", store=str(store))
    cmd_version_get(args)
    out = capsys.readouterr().out
    assert "/snaps/v2.json" in out


def test_cmd_get_missing_exits_1(store):
    args = make_args(name="ghost", store=str(store))
    with pytest.raises(SystemExit) as exc:
        cmd_version_get(args)
    assert exc.value.code == 1


def test_cmd_delete_success(store, capsys):
    add_version("prod", "/snaps/prod.json", store=store)
    args = make_args(name="prod", store=str(store))
    cmd_version_delete(args)
    out = capsys.readouterr().out
    assert "Deleted" in out


def test_cmd_delete_missing_exits_1(store):
    args = make_args(name="ghost", store=str(store))
    with pytest.raises(SystemExit) as exc:
        cmd_version_delete(args)
    assert exc.value.code == 1


def test_cmd_names_lists_all(store, capsys):
    add_version("prod", "/snaps/prod.json", store=store)
    add_version("staging", "/snaps/staging.json", store=store)
    args = make_args(store=str(store))
    cmd_version_names(args)
    out = capsys.readouterr().out
    assert "prod" in out
    assert "staging" in out


def test_cmd_names_empty(store, capsys):
    args = make_args(store=str(store))
    cmd_version_names(args)
    out = capsys.readouterr().out
    assert "No versioned" in out
