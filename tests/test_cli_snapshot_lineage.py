"""Tests for CLI commands in cli_snapshot_lineage."""
import argparse
import sys
import pytest
from pathlib import Path

from envpack import snapshot_lineage as lin
from envpack.cli_snapshot_lineage import (
    cmd_lineage_set,
    cmd_lineage_remove,
    cmd_lineage_parent,
    cmd_lineage_children,
    cmd_lineage_ancestors,
)


@pytest.fixture
def store(tmp_path):
    return tmp_path / "lineage.json"


def make_args(store, **kwargs):
    ns = argparse.Namespace(store=str(store), **kwargs)
    return ns


def test_cmd_set_prints_linked(store, capsys):
    args = make_args(store, snapshot="snap_b.json", parent="snap_a.json")
    cmd_lineage_set(args)
    out = capsys.readouterr().out
    assert "Linked" in out
    assert "snap_b.json" in out


def test_cmd_set_prints_updated_on_second_call(store, capsys):
    args = make_args(store, snapshot="snap_b.json", parent="snap_a.json")
    cmd_lineage_set(args)
    args2 = make_args(store, snapshot="snap_b.json", parent="snap_c.json")
    cmd_lineage_set(args2)
    out = capsys.readouterr().out
    assert "Updated" in out


def test_cmd_remove_success(store, capsys):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    args = make_args(store, snapshot="snap_b.json")
    cmd_lineage_remove(args)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_remove_missing_exits_1(store):
    args = make_args(store, snapshot="missing.json")
    with pytest.raises(SystemExit) as exc:
        cmd_lineage_remove(args)
    assert exc.value.code == 1


def test_cmd_parent_prints_parent(store, capsys):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    args = make_args(store, snapshot="snap_b.json")
    cmd_lineage_parent(args)
    out = capsys.readouterr().out
    assert "snap_a.json" in out


def test_cmd_parent_missing_exits_1(store):
    args = make_args(store, snapshot="missing.json")
    with pytest.raises(SystemExit) as exc:
        cmd_lineage_parent(args)
    assert exc.value.code == 1


def test_cmd_children_prints_children(store, capsys):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    lin.set_parent("snap_c.json", "snap_a.json", store=store)
    args = make_args(store, snapshot="snap_a.json")
    cmd_lineage_children(args)
    out = capsys.readouterr().out
    assert "snap_b.json" in out
    assert "snap_c.json" in out


def test_cmd_children_no_children_message(store, capsys):
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    args = make_args(store, snapshot="snap_b.json")
    cmd_lineage_children(args)
    out = capsys.readouterr().out
    assert "No children" in out


def test_cmd_ancestors_prints_chain(store, capsys):
    lin.set_parent("snap_c.json", "snap_b.json", store=store)
    lin.set_parent("snap_b.json", "snap_a.json", store=store)
    args = make_args(store, snapshot="snap_c.json")
    cmd_lineage_ancestors(args)
    out = capsys.readouterr().out
    assert "snap_b.json" in out
    assert "snap_a.json" in out
