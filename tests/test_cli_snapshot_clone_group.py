"""Tests for envpack.cli_snapshot_clone_group."""
import argparse
import sys

import pytest

from envpack.cli_snapshot_clone_group import (
    cmd_group_add,
    cmd_group_create,
    cmd_group_delete,
    cmd_group_list,
    cmd_group_remove,
    cmd_group_show,
)
from envpack.snapshot_clone_group import create_group, add_snapshot_to_group


@pytest.fixture()
def store(tmp_path):
    return tmp_path / "clone_groups.json"


def make_args(**kwargs):
    defaults = {"name": "g1", "description": "", "snapshot": "snap.json"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_create_prints_name(store, capsys):
    args = make_args(store=str(store))
    cmd_group_create(args)
    out = capsys.readouterr().out
    assert "g1" in out


def test_cmd_create_with_description(store, capsys):
    args = make_args(store=str(store), description="hello")
    cmd_group_create(args)
    from envpack.snapshot_clone_group import get_group
    entry = get_group("g1", store=store)
    assert entry["description"] == "hello"


def test_cmd_delete_success(store, capsys):
    create_group("g1", store=store)
    args = make_args(store=str(store))
    cmd_group_delete(args)
    out = capsys.readouterr().out
    assert "Deleted" in out


def test_cmd_delete_missing_exits_1(store):
    args = make_args(store=str(store))
    with pytest.raises(SystemExit) as exc:
        cmd_group_delete(args)
    assert exc.value.code == 1


def test_cmd_add_prints_added(store, capsys):
    create_group("g1", store=store)
    args = make_args(store=str(store), snapshot="snap.json")
    cmd_group_add(args)
    out = capsys.readouterr().out
    assert "Added" in out


def test_cmd_add_prints_already_present(store, capsys):
    create_group("g1", store=store)
    add_snapshot_to_group("g1", "snap.json", store=store)
    args = make_args(store=str(store), snapshot="snap.json")
    cmd_group_add(args)
    out = capsys.readouterr().out
    assert "already" in out


def test_cmd_add_missing_group_exits_1(store):
    args = make_args(store=str(store), snapshot="snap.json")
    with pytest.raises(SystemExit) as exc:
        cmd_group_add(args)
    assert exc.value.code == 1


def test_cmd_remove_success(store, capsys):
    create_group("g1", store=store)
    add_snapshot_to_group("g1", "snap.json", store=store)
    args = make_args(store=str(store), snapshot="snap.json")
    cmd_group_remove(args)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_show_lists_snapshots(store, capsys):
    create_group("g1", store=store)
    add_snapshot_to_group("g1", "snap.json", store=store)
    args = make_args(store=str(store))
    cmd_group_show(args)
    out = capsys.readouterr().out
    assert "snap.json" in out


def test_cmd_show_missing_exits_1(store):
    args = make_args(store=str(store))
    with pytest.raises(SystemExit) as exc:
        cmd_group_show(args)
    assert exc.value.code == 1


def test_cmd_list_empty(store, capsys):
    args = make_args(store=str(store))
    cmd_group_list(args)
    out = capsys.readouterr().out
    assert "No clone groups" in out


def test_cmd_list_shows_groups(store, capsys):
    create_group("alpha", store=store)
    create_group("beta", store=store)
    args = make_args(store=str(store))
    cmd_group_list(args)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out
