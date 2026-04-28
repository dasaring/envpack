"""Tests for envpack.snapshot_version."""

import json
import pytest
from pathlib import Path

from envpack.snapshot_version import (
    add_version,
    list_versions,
    get_version,
    delete_version_history,
    all_version_names,
)


@pytest.fixture
def store(tmp_path):
    return tmp_path / "versions.json"


def test_add_version_returns_entry(store):
    entry = add_version("prod", "/snaps/prod.json", store=store)
    assert entry["snapshot"] == "/snaps/prod.json"
    assert entry["label"] is None


def test_add_version_with_label(store):
    entry = add_version("prod", "/snaps/prod.json", label="v1", store=store)
    assert entry["label"] == "v1"


def test_add_version_creates_file(store):
    add_version("prod", "/snaps/prod.json", store=store)
    assert store.exists()


def test_add_version_file_is_valid_json(store):
    add_version("prod", "/snaps/prod.json", store=store)
    data = json.loads(store.read_text())
    assert "prod" in data


def test_add_multiple_versions_appends(store):
    add_version("prod", "/snaps/prod_v1.json", store=store)
    add_version("prod", "/snaps/prod_v2.json", store=store)
    versions = list_versions("prod", store=store)
    assert len(versions) == 2
    assert versions[0]["snapshot"] == "/snaps/prod_v1.json"
    assert versions[1]["snapshot"] == "/snaps/prod_v2.json"


def test_list_versions_empty_returns_empty_list(store):
    result = list_versions("nonexistent", store=store)
    assert result == []


def test_get_version_latest_by_default(store):
    add_version("prod", "/snaps/prod_v1.json", store=store)
    add_version("prod", "/snaps/prod_v2.json", store=store)
    entry = get_version("prod", store=store)
    assert entry["snapshot"] == "/snaps/prod_v2.json"


def test_get_version_by_index(store):
    add_version("prod", "/snaps/prod_v1.json", store=store)
    add_version("prod", "/snaps/prod_v2.json", store=store)
    entry = get_version("prod", index=0, store=store)
    assert entry["snapshot"] == "/snaps/prod_v1.json"


def test_get_version_missing_name_returns_none(store):
    result = get_version("ghost", store=store)
    assert result is None


def test_get_version_out_of_range_returns_none(store):
    add_version("prod", "/snaps/prod.json", store=store)
    result = get_version("prod", index=99, store=store)
    assert result is None


def test_delete_version_history_returns_true(store):
    add_version("prod", "/snaps/prod.json", store=store)
    assert delete_version_history("prod", store=store) is True


def test_delete_version_history_removes_entry(store):
    add_version("prod", "/snaps/prod.json", store=store)
    delete_version_history("prod", store=store)
    assert list_versions("prod", store=store) == []


def test_delete_version_history_missing_returns_false(store):
    assert delete_version_history("ghost", store=store) is False


def test_all_version_names_returns_all(store):
    add_version("prod", "/snaps/prod.json", store=store)
    add_version("staging", "/snaps/staging.json", store=store)
    names = all_version_names(store=store)
    assert set(names) == {"prod", "staging"}


def test_all_version_names_empty_store(store):
    assert all_version_names(store=store) == []
