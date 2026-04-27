"""Tests for envpack.snapshot_clone_group."""
import json

import pytest

from envpack.snapshot_clone_group import (
    add_snapshot_to_group,
    create_group,
    delete_group,
    get_group,
    list_groups,
    remove_snapshot_from_group,
)


@pytest.fixture()
def store(tmp_path):
    return tmp_path / "clone_groups.json"


def test_create_group_returns_entry(store):
    entry = create_group("mygroup", store=store)
    assert entry["name"] == "mygroup"
    assert entry["snapshots"] == []


def test_create_group_creates_file(store):
    create_group("g1", store=store)
    assert store.exists()


def test_create_group_file_is_valid_json(store):
    create_group("g1", store=store)
    data = json.loads(store.read_text())
    assert "g1" in data


def test_create_group_stores_description(store):
    create_group("g1", description="my desc", store=store)
    entry = get_group("g1", store=store)
    assert entry["description"] == "my desc"


def test_create_group_overwrites_existing(store):
    create_group("g1", store=store)
    add_snapshot_to_group("g1", "snap.json", store=store)
    create_group("g1", store=store)
    entry = get_group("g1", store=store)
    assert entry["snapshots"] == []


def test_delete_group_returns_true(store):
    create_group("g1", store=store)
    assert delete_group("g1", store=store) is True


def test_delete_group_returns_false_when_missing(store):
    assert delete_group("nonexistent", store=store) is False


def test_delete_group_removes_entry(store):
    create_group("g1", store=store)
    delete_group("g1", store=store)
    assert get_group("g1", store=store) is None


def test_add_snapshot_returns_true_for_new(store):
    create_group("g1", store=store)
    assert add_snapshot_to_group("g1", "a.json", store=store) is True


def test_add_snapshot_returns_false_for_duplicate(store):
    create_group("g1", store=store)
    add_snapshot_to_group("g1", "a.json", store=store)
    assert add_snapshot_to_group("g1", "a.json", store=store) is False


def test_add_snapshot_no_duplicates(store):
    create_group("g1", store=store)
    add_snapshot_to_group("g1", "a.json", store=store)
    add_snapshot_to_group("g1", "a.json", store=store)
    entry = get_group("g1", store=store)
    assert entry["snapshots"].count("a.json") == 1


def test_add_snapshot_to_missing_group_raises(store):
    with pytest.raises(KeyError):
        add_snapshot_to_group("ghost", "a.json", store=store)


def test_remove_snapshot_returns_true(store):
    create_group("g1", store=store)
    add_snapshot_to_group("g1", "a.json", store=store)
    assert remove_snapshot_from_group("g1", "a.json", store=store) is True


def test_remove_snapshot_returns_false_when_absent(store):
    create_group("g1", store=store)
    assert remove_snapshot_from_group("g1", "missing.json", store=store) is False


def test_list_groups_empty(store):
    assert list_groups(store=store) == []


def test_list_groups_returns_all(store):
    create_group("a", store=store)
    create_group("b", store=store)
    names = {g["name"] for g in list_groups(store=store)}
    assert names == {"a", "b"}
