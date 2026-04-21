"""Integration tests: scope + snapshot lifecycle."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from envpack.scope import (
    add_to_scope,
    remove_from_scope,
    get_snapshots_in_scope,
    list_scopes,
    find_scope_for_snapshot,
)
from envpack.snapshot import save, load


@pytest.fixture
def snapshot_path(tmp_path: Path) -> Path:
    path = tmp_path / "snap.json"
    save({"APP_ENV": "production", "DB_HOST": "localhost"}, path)
    return path


@pytest.fixture
def scope_file(tmp_path: Path) -> Path:
    return tmp_path / "scopes.json"


def test_scope_references_valid_snapshot(snapshot_path, scope_file):
    add_to_scope("prod", str(snapshot_path), scope_file)
    paths = get_snapshots_in_scope("prod", scope_file)
    assert str(snapshot_path) in paths
    snap = load(Path(paths[0]))
    assert snap["APP_ENV"] == "production"


def test_scope_lifecycle(snapshot_path, scope_file):
    add_to_scope("dev", str(snapshot_path), scope_file)
    assert "dev" in list_scopes(scope_file)

    found = find_scope_for_snapshot(str(snapshot_path), scope_file)
    assert found == "dev"

    remove_from_scope("dev", str(snapshot_path), scope_file)
    assert "dev" not in list_scopes(scope_file)


def test_multiple_scopes_independent(tmp_path, scope_file):
    p1 = tmp_path / "snap1.json"
    p2 = tmp_path / "snap2.json"
    save({"X": "1"}, p1)
    save({"Y": "2"}, p2)

    add_to_scope("alpha", str(p1), scope_file)
    add_to_scope("beta", str(p2), scope_file)

    assert get_snapshots_in_scope("alpha", scope_file) == [str(p1)]
    assert get_snapshots_in_scope("beta", scope_file) == [str(p2)]


def test_scope_file_persists_across_calls(snapshot_path, scope_file):
    add_to_scope("ci", str(snapshot_path), scope_file)
    # Re-read from disk by calling again with same file
    scopes = list_scopes(scope_file)
    assert "ci" in scopes
    raw = json.loads(scope_file.read_text())
    assert "ci" in raw
