"""Tests for envpack.bookmark and envpack.cli_bookmark."""

from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path

import pytest

from envpack.bookmark import (
    add_bookmark,
    remove_bookmark,
    resolve_bookmark,
    list_bookmarks,
    clear_bookmarks,
)
from envpack.cli_bookmark import (
    cmd_bookmark_add,
    cmd_bookmark_remove,
    cmd_bookmark_resolve,
    cmd_bookmark_list,
    cmd_bookmark_clear,
)


@pytest.fixture
def bstore(tmp_path: Path) -> Path:
    return tmp_path / "bookmarks.json"


def make_args(store: Path, **kwargs) -> argparse.Namespace:
    return argparse.Namespace(store=str(store), **kwargs)


# --- bookmark module tests ---

def test_add_bookmark_returns_true_for_new(bstore):
    assert add_bookmark("dev", "/tmp/dev.json", store=bstore) is True


def test_add_bookmark_creates_file(bstore):
    add_bookmark("dev", "/tmp/dev.json", store=bstore)
    assert bstore.exists()


def test_add_bookmark_file_is_valid_json(bstore):
    add_bookmark("dev", "/tmp/dev.json", store=bstore)
    data = json.loads(bstore.read_text())
    assert isinstance(data, dict)


def test_add_bookmark_returns_false_when_updated(bstore):
    add_bookmark("dev", "/tmp/dev.json", store=bstore)
    assert add_bookmark("dev", "/tmp/dev2.json", store=bstore) is False


def test_resolve_bookmark_returns_path(bstore):
    add_bookmark("prod", "/tmp/prod.json", store=bstore)
    assert resolve_bookmark("prod", store=bstore) == "/tmp/prod.json"


def test_resolve_bookmark_missing_returns_none(bstore):
    assert resolve_bookmark("ghost", store=bstore) is None


def test_remove_bookmark_returns_true(bstore):
    add_bookmark("staging", "/tmp/s.json", store=bstore)
    assert remove_bookmark("staging", store=bstore) is True


def test_remove_bookmark_missing_returns_false(bstore):
    assert remove_bookmark("nope", store=bstore) is False


def test_list_bookmarks_returns_all(bstore):
    add_bookmark("a", "/a.json", store=bstore)
    add_bookmark("b", "/b.json", store=bstore)
    bms = list_bookmarks(store=bstore)
    assert bms == {"a": "/a.json", "b": "/b.json"}


def test_clear_bookmarks_returns_count(bstore):
    add_bookmark("x", "/x.json", store=bstore)
    add_bookmark("y", "/y.json", store=bstore)
    assert clear_bookmarks(store=bstore) == 2
    assert list_bookmarks(store=bstore) == {}


# --- CLI tests ---

def test_cmd_bookmark_add_prints_created(bstore, capsys):
    cmd_bookmark_add(make_args(bstore, name="ci", path="/ci.json"))
    out = capsys.readouterr().out
    assert "Created" in out and "ci" in out


def test_cmd_bookmark_add_prints_updated(bstore, capsys):
    add_bookmark("ci", "/old.json", store=bstore)
    cmd_bookmark_add(make_args(bstore, name="ci", path="/new.json"))
    out = capsys.readouterr().out
    assert "Updated" in out


def test_cmd_bookmark_remove_success(bstore, capsys):
    add_bookmark("tmp", "/t.json", store=bstore)
    cmd_bookmark_remove(make_args(bstore, name="tmp"))
    assert "Removed" in capsys.readouterr().out


def test_cmd_bookmark_remove_missing_exits_1(bstore):
    with pytest.raises(SystemExit) as exc:
        cmd_bookmark_remove(make_args(bstore, name="missing"))
    assert exc.value.code == 1


def test_cmd_bookmark_resolve_prints_path(bstore, capsys):
    add_bookmark("local", "/local.json", store=bstore)
    cmd_bookmark_resolve(make_args(bstore, name="local"))
    assert "/local.json" in capsys.readouterr().out


def test_cmd_bookmark_resolve_missing_exits_1(bstore):
    with pytest.raises(SystemExit) as exc:
        cmd_bookmark_resolve(make_args(bstore, name="none"))
    assert exc.value.code == 1


def test_cmd_bookmark_list_empty(bstore, capsys):
    cmd_bookmark_list(make_args(bstore))
    assert "No bookmarks" in capsys.readouterr().out


def test_cmd_bookmark_clear_prints_count(bstore, capsys):
    add_bookmark("a", "/a.json", store=bstore)
    cmd_bookmark_clear(make_args(bstore))
    assert "1" in capsys.readouterr().out
