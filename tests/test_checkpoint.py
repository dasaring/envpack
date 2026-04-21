"""Tests for envpack.checkpoint."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.checkpoint import (
    create_checkpoint,
    delete_checkpoint,
    get_checkpoint,
    list_checkpoints,
)


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "checkpoints.json"


def test_create_checkpoint_returns_entry(store: Path) -> None:
    entry = create_checkpoint("v1", "/tmp/snap.json", store=store)
    assert entry["snapshot"] == "/tmp/snap.json"


def test_create_checkpoint_creates_file(store: Path) -> None:
    create_checkpoint("v1", "/tmp/snap.json", store=store)
    assert store.exists()


def test_create_checkpoint_file_is_valid_json(store: Path) -> None:
    create_checkpoint("v1", "/tmp/snap.json", store=store)
    data = json.loads(store.read_text())
    assert "v1" in data


def test_create_checkpoint_stores_description(store: Path) -> None:
    create_checkpoint("v1", "/tmp/snap.json", description="initial", store=store)
    entry = get_checkpoint("v1", store=store)
    assert entry is not None
    assert entry["description"] == "initial"


def test_create_checkpoint_overwrites_existing(store: Path) -> None:
    create_checkpoint("v1", "/tmp/old.json", store=store)
    create_checkpoint("v1", "/tmp/new.json", store=store)
    entry = get_checkpoint("v1", store=store)
    assert entry["snapshot"] == "/tmp/new.json"


def test_get_checkpoint_missing_returns_none(store: Path) -> None:
    assert get_checkpoint("missing", store=store) is None


def test_delete_checkpoint_returns_true(store: Path) -> None:
    create_checkpoint("v1", "/tmp/snap.json", store=store)
    assert delete_checkpoint("v1", store=store) is True


def test_delete_checkpoint_removes_entry(store: Path) -> None:
    create_checkpoint("v1", "/tmp/snap.json", store=store)
    delete_checkpoint("v1", store=store)
    assert get_checkpoint("v1", store=store) is None


def test_delete_checkpoint_missing_returns_false(store: Path) -> None:
    assert delete_checkpoint("ghost", store=store) is False


def test_list_checkpoints_empty(store: Path) -> None:
    assert list_checkpoints(store=store) == {}


def test_list_checkpoints_returns_all(store: Path) -> None:
    create_checkpoint("a", "/tmp/a.json", store=store)
    create_checkpoint("b", "/tmp/b.json", store=store)
    result = list_checkpoints(store=store)
    assert set(result.keys()) == {"a", "b"}
