"""Tests for envpack.snapshot_promote."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.snapshot_promote import PromoteError, promote_snapshot, promotion_diff


@pytest.fixture()
def snap(tmp_path) -> Path:
    p = tmp_path / "dev.json"
    p.write_text(json.dumps({"APP_ENV": "dev", "DB_URL": "sqlite:///dev.db", "SECRET": "s3cr3t"}))
    return p


def test_promote_creates_destination(snap, tmp_path):
    dest = tmp_path / "staging" / "snap.json"
    result = promote_snapshot(snap, dest)
    assert result == dest
    assert dest.exists()


def test_promote_content_matches_source(snap, tmp_path):
    dest = tmp_path / "staging.json"
    promote_snapshot(snap, dest)
    assert json.loads(dest.read_text()) == json.loads(snap.read_text())


def test_promote_strip_keys(snap, tmp_path):
    dest = tmp_path / "staging.json"
    promote_snapshot(snap, dest, strip_keys=["SECRET"])
    data = json.loads(dest.read_text())
    assert "SECRET" not in data
    assert "APP_ENV" in data


def test_promote_add_keys(snap, tmp_path):
    dest = tmp_path / "staging.json"
    promote_snapshot(snap, dest, add_keys={"STAGE": "staging"})
    data = json.loads(dest.read_text())
    assert data["STAGE"] == "staging"


def test_promote_strip_and_add(snap, tmp_path):
    dest = tmp_path / "prod.json"
    promote_snapshot(snap, dest, strip_keys=["SECRET"], add_keys={"APP_ENV": "production"})
    data = json.loads(dest.read_text())
    assert "SECRET" not in data
    assert data["APP_ENV"] == "production"


def test_promote_missing_source_raises(tmp_path):
    with pytest.raises(PromoteError, match="not found"):
        promote_snapshot(tmp_path / "missing.json", tmp_path / "dest.json")


def test_promote_no_overwrite_raises(snap, tmp_path):
    dest = tmp_path / "dest.json"
    dest.write_text(json.dumps({"X": "1"}))
    with pytest.raises(PromoteError, match="already exists"):
        promote_snapshot(snap, dest)


def test_promote_overwrite_flag_works(snap, tmp_path):
    dest = tmp_path / "dest.json"
    dest.write_text(json.dumps({"X": "1"}))
    promote_snapshot(snap, dest, overwrite=True)
    data = json.loads(dest.read_text())
    assert "APP_ENV" in data


def test_promote_does_not_mutate_source(snap, tmp_path):
    original = json.loads(snap.read_text())
    dest = tmp_path / "dest.json"
    promote_snapshot(snap, dest, strip_keys=["SECRET"], add_keys={"NEW": "val"})
    assert json.loads(snap.read_text()) == original


def test_promotion_diff_added_keys(snap, tmp_path):
    dest = tmp_path / "dest.json"
    diff = promotion_diff(snap, dest)
    assert set(diff["added"]) == {"APP_ENV", "DB_URL", "SECRET"}
    assert diff["removed"] == []


def test_promotion_diff_changed_keys(snap, tmp_path):
    dest = tmp_path / "dest.json"
    dest.write_text(json.dumps({"APP_ENV": "staging", "DB_URL": "sqlite:///dev.db"}))
    diff = promotion_diff(snap, dest)
    assert "APP_ENV" in diff["changed"]
    assert "DB_URL" in diff["unchanged"]
    assert "SECRET" in diff["added"]
