"""Tests for envpack.snapshot_set and envpack.cli_snapshot_set."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from envpack.snapshot_set import (
    add_snapshot_to_set,
    create_set,
    delete_set,
    get_set,
    list_sets,
    remove_snapshot_from_set,
)
from envpack.cli_snapshot_set import (
    cmd_set_add,
    cmd_set_create,
    cmd_set_delete,
    cmd_set_list,
    cmd_set_remove,
    cmd_set_show,
)


@pytest.fixture()
def store(tmp_path):
    return tmp_path / "sets.json"


# --- snapshot_set module ---

def test_create_set_returns_entry(store):
    entry = create_set("prod", description="production", store=store)
    assert entry["name"] == "prod"
    assert entry["description"] == "production"
    assert entry["snapshots"] == []


def test_create_set_creates_file(store):
    create_set("prod", store=store)
    assert store.exists()


def test_create_set_file_is_valid_json(store):
    create_set("prod", store=store)
    data = json.loads(store.read_text())
    assert "prod" in data


def test_create_set_overwrites_existing(store):
    create_set("prod", description="old", store=store)
    create_set("prod", description="new", store=store)
    entry = get_set("prod", store=store)
    assert entry["description"] == "new"


def test_delete_set_returns_true(store):
    create_set("prod", store=store)
    assert delete_set("prod", store=store) is True


def test_delete_set_returns_false_when_missing(store):
    assert delete_set("nonexistent", store=store) is False


def test_add_snapshot_no_duplicate(store):
    create_set("dev", store=store)
    add_snapshot_to_set("dev", "snap.json", store=store)
    result = add_snapshot_to_set("dev", "snap.json", store=store)
    assert result is False
    entry = get_set("dev", store=store)
    assert entry["snapshots"].count("snap.json") == 1


def test_add_snapshot_raises_for_missing_set(store):
    with pytest.raises(KeyError):
        add_snapshot_to_set("ghost", "snap.json", store=store)


def test_remove_snapshot_returns_false_when_absent(store):
    create_set("dev", store=store)
    assert remove_snapshot_from_set("dev", "missing.json", store=store) is False


def test_list_sets_returns_all(store):
    create_set("a", store=store)
    create_set("b", store=store)
    names = {s["name"] for s in list_sets(store=store)}
    assert names == {"a", "b"}


def test_get_set_returns_none_for_missing(store):
    assert get_set("nope", store=store) is None


# --- CLI commands ---

def make_args(store, **kwargs):
    return SimpleNamespace(store=store, **kwargs)


def test_cmd_create_prints_created(store, capsys):
    cmd_set_create(make_args(store, name="ci", description=""))
    out = capsys.readouterr().out
    assert "Created set 'ci'" in out


def test_cmd_delete_success(store, capsys):
    create_set("ci", store=store)
    cmd_set_delete(make_args(store, name="ci"))
    assert get_set("ci", store=store) is None


def test_cmd_delete_missing_exits_1(store):
    with pytest.raises(SystemExit) as exc:
        cmd_set_delete(make_args(store, name="ghost"))
    assert exc.value.code == 1


def test_cmd_add_prints_added(store, capsys):
    create_set("ci", store=store)
    cmd_set_add(make_args(store, name="ci", snapshot="snap.json"))
    out = capsys.readouterr().out
    assert "Added" in out


def test_cmd_show_lists_snapshots(store, capsys):
    create_set("ci", store=store)
    add_snapshot_to_set("ci", "a.json", store=store)
    cmd_set_show(make_args(store, name="ci"))
    out = capsys.readouterr().out
    assert "a.json" in out


def test_cmd_list_empty(store, capsys):
    cmd_set_list(make_args(store))
    out = capsys.readouterr().out
    assert "No snapshot sets" in out
