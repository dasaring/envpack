"""Integration tests: snapshot_search works end-to-end with real snapshot files."""

from __future__ import annotations

import os

import pytest

from envpack.snapshot import save
from envpack.snapshot_search import search_by_key, search_by_value, search_snapshots


@pytest.fixture()
def populated_dir(tmp_path):
    """Write real snapshots via envpack.snapshot.save."""
    snaps = [
        ("prod.json", {"DATABASE_URL": "postgres://prod", "LOG_LEVEL": "warn"}),
        ("staging.json", {"DATABASE_URL": "postgres://staging", "LOG_LEVEL": "debug"}),
        ("dev.json", {"DATABASE_URL": "sqlite:///dev.db", "DEBUG": "true"}),
    ]
    for fname, env in snaps:
        save(env, str(tmp_path / fname))
    return tmp_path


def test_search_by_key_finds_all_with_key(populated_dir):
    results = search_by_key(str(populated_dir), "DATABASE_URL")
    assert len(results) == 3


def test_search_by_key_partial_glob(populated_dir):
    results = search_by_key(str(populated_dir), "LOG_*")
    names = {os.path.basename(r.path) for r in results}
    assert names == {"prod.json", "staging.json"}


def test_search_by_value_finds_sqlite(populated_dir):
    results = search_by_value(str(populated_dir), "*sqlite*")
    assert len(results) == 1
    assert os.path.basename(results[0].path) == "dev.json"


def test_search_combined_narrows_results(populated_dir):
    results = search_snapshots(
        str(populated_dir),
        key_pattern="DATABASE_URL",
        value_pattern="*postgres*",
    )
    names = {os.path.basename(r.path) for r in results}
    assert names == {"prod.json", "staging.json"}
    assert "dev.json" not in names


def test_search_returns_matched_keys(populated_dir):
    results = search_by_key(str(populated_dir), "DEBUG")
    assert len(results) == 1
    assert "DEBUG" in results[0].matched_keys
