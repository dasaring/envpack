"""Tests for envpack.cli_alias."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from envpack.alias import add_alias
from envpack.cli_alias import (
    cmd_alias_add,
    cmd_alias_list,
    cmd_alias_remove,
    cmd_alias_resolve,
)


@pytest.fixture()
def alias_file(tmp_path: Path) -> Path:
    return tmp_path / "aliases.json"


def make_args(alias_file: Path, **kwargs) -> argparse.Namespace:
    defaults = {"alias_file": str(alias_file)}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_alias_add_prints_created(alias_file, capsys):
    args = make_args(alias_file, name="prod", snapshot="/snaps/prod.json")
    cmd_alias_add(args)
    out = capsys.readouterr().out
    assert "Created" in out
    assert "prod" in out


def test_cmd_alias_add_prints_updated(alias_file, capsys):
    add_alias("prod", "/snaps/prod.json", alias_file)
    args = make_args(alias_file, name="prod", snapshot="/snaps/prod_v2.json")
    cmd_alias_add(args)
    out = capsys.readouterr().out
    assert "Updated" in out


def test_cmd_alias_remove_success(alias_file, capsys):
    add_alias("dev", "/snaps/dev.json", alias_file)
    args = make_args(alias_file, name="dev")
    cmd_alias_remove(args)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_alias_remove_missing(alias_file, capsys):
    args = make_args(alias_file, name="ghost")
    cmd_alias_remove(args)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_alias_resolve_found(alias_file, capsys):
    add_alias("staging", "/snaps/staging.json", alias_file)
    args = make_args(alias_file, name="staging")
    cmd_alias_resolve(args)
    out = capsys.readouterr().out.strip()
    assert out == "/snaps/staging.json"


def test_cmd_alias_resolve_missing(alias_file, capsys):
    args = make_args(alias_file, name="nope")
    cmd_alias_resolve(args)
    out = capsys.readouterr().out
    assert "No alias" in out


def test_cmd_alias_list_empty(alias_file, capsys):
    args = make_args(alias_file)
    cmd_alias_list(args)
    out = capsys.readouterr().out
    assert "No aliases" in out


def test_cmd_alias_list_shows_entries(alias_file, capsys):
    add_alias("prod", "/snaps/prod.json", alias_file)
    add_alias("dev", "/snaps/dev.json", alias_file)
    args = make_args(alias_file)
    cmd_alias_list(args)
    out = capsys.readouterr().out
    assert "prod" in out
    assert "dev" in out
