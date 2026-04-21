"""Tests for envpack.cli_scope CLI commands."""

from __future__ import annotations

import argparse
import pytest
from pathlib import Path

from envpack.cli_scope import (
    cmd_scope_add,
    cmd_scope_remove,
    cmd_scope_list,
    cmd_scope_show,
    cmd_scope_find,
)
from envpack.scope import add_to_scope


@pytest.fixture
def scope_file(tmp_path: Path) -> Path:
    return tmp_path / "scopes.json"


def make_args(scope_file: Path, **kwargs) -> argparse.Namespace:
    return argparse.Namespace(scope_file=str(scope_file), **kwargs)


def test_cmd_scope_add_prints_added(scope_file, capsys):
    args = make_args(scope_file, scope="dev", snapshot="snap.json")
    cmd_scope_add(args)
    out = capsys.readouterr().out
    assert "Added" in out
    assert "dev" in out


def test_cmd_scope_add_prints_already_present(scope_file, capsys):
    add_to_scope("dev", "snap.json", scope_file)
    args = make_args(scope_file, scope="dev", snapshot="snap.json")
    cmd_scope_add(args)
    out = capsys.readouterr().out
    assert "already" in out


def test_cmd_scope_remove_success(scope_file, capsys):
    add_to_scope("prod", "snap.json", scope_file)
    args = make_args(scope_file, scope="prod", snapshot="snap.json")
    cmd_scope_remove(args)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_scope_remove_not_found(scope_file, capsys):
    args = make_args(scope_file, scope="prod", snapshot="missing.json")
    cmd_scope_remove(args)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_scope_list_empty(scope_file, capsys):
    args = make_args(scope_file)
    cmd_scope_list(args)
    out = capsys.readouterr().out
    assert "No scopes" in out


def test_cmd_scope_list_shows_scopes(scope_file, capsys):
    add_to_scope("dev", "a.json", scope_file)
    add_to_scope("prod", "b.json", scope_file)
    args = make_args(scope_file)
    cmd_scope_list(args)
    out = capsys.readouterr().out
    assert "dev" in out
    assert "prod" in out


def test_cmd_scope_show_lists_snapshots(scope_file, capsys):
    add_to_scope("dev", "snap_x.json", scope_file)
    args = make_args(scope_file, scope="dev")
    cmd_scope_show(args)
    out = capsys.readouterr().out
    assert "snap_x.json" in out


def test_cmd_scope_show_empty(scope_file, capsys):
    args = make_args(scope_file, scope="ghost")
    cmd_scope_show(args)
    out = capsys.readouterr().out
    assert "empty" in out or "does not exist" in out


def test_cmd_scope_find_found(scope_file, capsys):
    add_to_scope("staging", "snap_s.json", scope_file)
    args = make_args(scope_file, snapshot="snap_s.json")
    cmd_scope_find(args)
    out = capsys.readouterr().out
    assert "staging" in out


def test_cmd_scope_find_not_found(scope_file, capsys):
    args = make_args(scope_file, snapshot="unknown.json")
    cmd_scope_find(args)
    out = capsys.readouterr().out
    assert "No scope" in out
