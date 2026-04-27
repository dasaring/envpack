"""Tests for envpack.snapshot_mask."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.snapshot_mask import (
    DEFAULT_MASK,
    MaskError,
    mask_by_keys,
    mask_by_pattern,
    mask_file,
    masked_keys,
)

SNAPSHOT = {
    "DB_PASSWORD": "secret",
    "API_KEY": "abc123",
    "APP_ENV": "production",
    "PORT": "8080",
}


def test_mask_by_keys_replaces_exact_keys():
    result = mask_by_keys(SNAPSHOT, ["DB_PASSWORD", "API_KEY"])
    assert result["DB_PASSWORD"] == DEFAULT_MASK
    assert result["API_KEY"] == DEFAULT_MASK


def test_mask_by_keys_leaves_other_keys_unchanged():
    result = mask_by_keys(SNAPSHOT, ["DB_PASSWORD"])
    assert result["APP_ENV"] == "production"
    assert result["PORT"] == "8080"


def test_mask_by_keys_does_not_mutate_original():
    original = dict(SNAPSHOT)
    mask_by_keys(original, ["DB_PASSWORD"])
    assert original["DB_PASSWORD"] == "secret"


def test_mask_by_keys_custom_mask():
    result = mask_by_keys(SNAPSHOT, ["PORT"], mask="REDACTED")
    assert result["PORT"] == "REDACTED"


def test_mask_by_keys_missing_key_is_ignored():
    result = mask_by_keys(SNAPSHOT, ["NONEXISTENT"])
    assert set(result.keys()) == set(SNAPSHOT.keys())


def test_mask_by_pattern_matches_regex():
    result = mask_by_pattern(SNAPSHOT, r"(PASSWORD|KEY)$")
    assert result["DB_PASSWORD"] == DEFAULT_MASK
    assert result["API_KEY"] == DEFAULT_MASK
    assert result["APP_ENV"] == "production"


def test_mask_by_pattern_no_match_returns_unchanged():
    result = mask_by_pattern(SNAPSHOT, r"^NONEXISTENT")
    assert result == SNAPSHOT


def test_mask_by_pattern_invalid_regex_raises():
    with pytest.raises(MaskError, match="Invalid pattern"):
        mask_by_pattern(SNAPSHOT, r"[invalid")


def test_masked_keys_returns_masked_list():
    snap = {"A": DEFAULT_MASK, "B": "value", "C": DEFAULT_MASK}
    assert sorted(masked_keys(snap)) == ["A", "C"]


def test_masked_keys_empty_when_none_masked():
    assert masked_keys(SNAPSHOT) == []


def test_mask_file_overwrites_source(tmp_path):
    snap_path = tmp_path / "snap.json"
    snap_path.write_text(json.dumps(SNAPSHOT))
    result = mask_file(snap_path, keys=["DB_PASSWORD"])
    assert result == snap_path
    data = json.loads(snap_path.read_text())
    assert data["DB_PASSWORD"] == DEFAULT_MASK


def test_mask_file_writes_to_output(tmp_path):
    snap_path = tmp_path / "snap.json"
    out_path = tmp_path / "masked.json"
    snap_path.write_text(json.dumps(SNAPSHOT))
    mask_file(snap_path, keys=["API_KEY"], output=out_path)
    data = json.loads(out_path.read_text())
    assert data["API_KEY"] == DEFAULT_MASK
    # source unchanged
    original = json.loads(snap_path.read_text())
    assert original["API_KEY"] == "abc123"


def test_mask_file_missing_source_raises(tmp_path):
    with pytest.raises(MaskError, match="not found"):
        mask_file(tmp_path / "missing.json", keys=["X"])


def test_mask_file_applies_both_keys_and_pattern(tmp_path):
    snap_path = tmp_path / "snap.json"
    snap_path.write_text(json.dumps(SNAPSHOT))
    mask_file(snap_path, keys=["PORT"], pattern=r"PASSWORD")
    data = json.loads(snap_path.read_text())
    assert data["PORT"] == DEFAULT_MASK
    assert data["DB_PASSWORD"] == DEFAULT_MASK
    assert data["APP_ENV"] == "production"
