"""Integration tests for snapshot clone group lifecycle."""
import json
from pathlib import Path

import pytest

from envpack.snapshot_clone_group import (
    add_snapshot_to_group,
    create_group,
    delete_group,
    get_group,
    list_groups,
    remove_snapshot_from_group,
)
from envpack.snapshot import save


@pytest.fixture()
def snapshot_path(tmp_path):
    p = tmp_path / "env_snapshot.json"
    save({"APP_ENV": "production", "DB_URL": "sqlite:///prod.db"}, str(p))
    return str(p)


@pytest.fixture()
def store(tmp_path):
    return tmp_path / "clone_groups.json"


def test_group_references_valid_snapshot(snapshot_path, store):
    create_group("prod", store=store)
    add_snapshot_to_group("prod", snapshot_path, store=store)
    entry = get_group("prod", store=store)
    assert snapshot_path in entry["snapshots"]
    assert Path(snapshot_path).exists()


def test_group_lifecycle(snapshot_path, store):
    create_group("ci", description="CI snapshots", store=store)
    add_snapshot_to_group("ci", snapshot_path, store=store)
    entry = get_group("ci", store=store)
    assert len(entry["snapshots"]) == 1

    remove_snapshot_from_group("ci", snapshot_path, store=store)
    entry = get_group("ci", store=store)
    assert entry["snapshots"] == []

    delete_group("ci", store=store)
    assert get_group("ci", store=store) is None


def test_multiple_groups_independent(tmp_path, store):
    snap1 = str(tmp_path / "s1.json")
    snap2 = str(tmp_path / "s2.json")
    save({"X": "1"}, snap1)
    save({"Y": "2"}, snap2)

    create_group("g1", store=store)
    create_group("g2", store=store)
    add_snapshot_to_group("g1", snap1, store=store)
    add_snapshot_to_group("g2", snap2, store=store)

    assert get_group("g1", store=store)["snapshots"] == [snap1]
    assert get_group("g2", store=store)["snapshots"] == [snap2]


def test_group_count_in_list(store):
    create_group("a", store=store)
    create_group("b", store=store)
    groups = list_groups(store=store)
    assert len(groups) == 2
    names = {g["name"] for g in groups}
    assert names == {"a", "b"}
