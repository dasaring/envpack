"""Integration tests for snapshot versioning: end-to-end lifecycle."""

import json
import pytest
from pathlib import Path

from envpack.snapshot import save
from envpack.snapshot_version import (
    add_version,
    list_versions,
    get_version,
    delete_version_history,
    all_version_names,
)


@pytest.fixture
def snapshot_path(tmp_path):
    path = tmp_path / "env.json"
    save({"APP_ENV": "production", "PORT": "8080"}, str(path))
    return path


@pytest.fixture
def store(tmp_path):
    return tmp_path / "versions.json"


def test_version_references_existing_snapshot(snapshot_path, store):
    entry = add_version("prod", str(snapshot_path), store=store)
    snap_path = Path(entry["snapshot"])
    assert snap_path.exists()
    data = json.loads(snap_path.read_text())
    assert data["APP_ENV"] == "production"


def test_version_lifecycle(snapshot_path, store):
    add_version("prod", str(snapshot_path), label="v1", store=store)
    add_version("prod", str(snapshot_path), label="v2", store=store)

    versions = list_versions("prod", store=store)
    assert len(versions) == 2

    latest = get_version("prod", store=store)
    assert latest["label"] == "v2"

    first = get_version("prod", index=0, store=store)
    assert first["label"] == "v1"

    delete_version_history("prod", store=store)
    assert list_versions("prod", store=store) == []


def test_multiple_names_independent(snapshot_path, store):
    add_version("prod", str(snapshot_path), store=store)
    add_version("staging", str(snapshot_path), store=store)
    add_version("staging", str(snapshot_path), store=store)

    assert len(list_versions("prod", store=store)) == 1
    assert len(list_versions("staging", store=store)) == 2
    assert set(all_version_names(store=store)) == {"prod", "staging"}

    delete_version_history("prod", store=store)
    assert all_version_names(store=store) == ["staging"]
