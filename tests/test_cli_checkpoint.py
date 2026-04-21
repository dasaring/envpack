"""Tests for envpack.cli_checkpoint."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from envpack.checkpoint import create_checkpoint
from envpack.cli_checkpoint import (
    cmd_checkpoint_create,
    cmd_checkpoint_delete,
    cmd_checkpoint_list,
    cmd_checkpoint_show,
)


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "checkpoints.json"


def make_args(**kwargs) -> argparse.Namespace:
    defaults = {"name": "v1", "snapshot": "/tmp/snap.json", "description": "", "store": ""}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_create_prints_name(capsys, store: Path) -> None:
    args = make_args(name="release", snapshot="/tmp/r.json", store=str(store))
    cmd_checkpoint_create(args)
    out = capsys.readouterr().out
    assert "release" in out
    assert "/tmp/r.json" in out


def test_cmd_delete_success(capsys, store: Path) -> None:
    create_checkpoint("v1", "/tmp/snap.json", store=store)
    args = make_args(name="v1", store=str(store))
    cmd_checkpoint_delete(args)
    out = capsys.readouterr().out
    assert "v1" in out


def test_cmd_delete_missing_exits_1(store: Path) -> None:
    args = make_args(name="ghost", store=str(store))
    with pytest.raises(SystemExit) as exc:
        cmd_checkpoint_delete(args)
    assert exc.value.code == 1


def test_cmd_show_prints_snapshot(capsys, store: Path) -> None:
    create_checkpoint("v1", "/tmp/snap.json", description="my snap", store=store)
    args = make_args(name="v1", store=str(store))
    cmd_checkpoint_show(args)
    out = capsys.readouterr().out
    assert "/tmp/snap.json" in out
    assert "my snap" in out


def test_cmd_show_missing_exits_1(store: Path) -> None:
    args = make_args(name="ghost", store=str(store))
    with pytest.raises(SystemExit) as exc:
        cmd_checkpoint_show(args)
    assert exc.value.code == 1


def test_cmd_list_empty(capsys, store: Path) -> None:
    args = make_args(store=str(store))
    cmd_checkpoint_list(args)
    out = capsys.readouterr().out
    assert "No checkpoints" in out


def test_cmd_list_shows_all(capsys, store: Path) -> None:
    create_checkpoint("a", "/tmp/a.json", store=store)
    create_checkpoint("b", "/tmp/b.json", store=store)
    args = make_args(store=str(store))
    cmd_checkpoint_list(args)
    out = capsys.readouterr().out
    assert "a" in out
    assert "b" in out
