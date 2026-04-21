"""Tests for envpack.profile module."""

import json
import pytest
from pathlib import Path

from envpack.profile import (
    create_profile,
    delete_profile,
    add_snapshot_to_profile,
    get_profile,
    list_profiles,
)


@pytest.fixture
def profiles_file(tmp_path):
    return tmp_path / "profiles.json"


def test_create_profile_new(profiles_file):
    result = create_profile("dev", ["snap1.json", "snap2.json"], profiles_file)
    assert result == ["snap1.json", "snap2.json"]


def test_create_profile_creates_file(profiles_file):
    create_profile("dev", ["snap1.json"], profiles_file)
    assert profiles_file.exists()


def test_create_profile_file_is_valid_json(profiles_file):
    create_profile("dev", ["snap1.json"], profiles_file)
    data = json.loads(profiles_file.read_text())
    assert "dev" in data


def test_create_profile_overwrites_existing(profiles_file):
    create_profile("dev", ["old.json"], profiles_file)
    create_profile("dev", ["new.json"], profiles_file)
    result = get_profile("dev", profiles_file)
    assert result == ["new.json"]


def test_create_profile_empty_paths(profiles_file):
    result = create_profile("empty", [], profiles_file)
    assert result == []


def test_delete_profile_returns_true(profiles_file):
    create_profile("staging", ["s.json"], profiles_file)
    assert delete_profile("staging", profiles_file) is True


def test_delete_profile_removes_entry(profiles_file):
    create_profile("staging", ["s.json"], profiles_file)
    delete_profile("staging", profiles_file)
    assert get_profile("staging", profiles_file) is None


def test_delete_nonexistent_profile_returns_false(profiles_file):
    assert delete_profile("ghost", profiles_file) is False


def test_add_snapshot_to_new_profile(profiles_file):
    result = add_snapshot_to_profile("prod", "snap_a.json", profiles_file)
    assert "snap_a.json" in result


def test_add_snapshot_no_duplicates(profiles_file):
    add_snapshot_to_profile("prod", "snap_a.json", profiles_file)
    result = add_snapshot_to_profile("prod", "snap_a.json", profiles_file)
    assert result.count("snap_a.json") == 1


def test_add_multiple_snapshots(profiles_file):
    add_snapshot_to_profile("prod", "snap_a.json", profiles_file)
    result = add_snapshot_to_profile("prod", "snap_b.json", profiles_file)
    assert len(result) == 2


def test_get_profile_not_found(profiles_file):
    assert get_profile("missing", profiles_file) is None


def test_list_profiles_empty(profiles_file):
    assert list_profiles(profiles_file) == []


def test_list_profiles_returns_names(profiles_file):
    create_profile("dev", [], profiles_file)
    create_profile("prod", [], profiles_file)
    names = list_profiles(profiles_file)
    assert set(names) == {"dev", "prod"}
