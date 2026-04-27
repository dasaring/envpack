"""Tests for envpack.snapshot_trim."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.snapshot_trim import (
    TrimError,
    trim_by_keys,
    trim_by_pattern,
    trim_by_prefix,
    trim_file,
    trim_snapshot,
)


SAMPLE = {
    "APP_NAME": "myapp",
    "APP_ENV": "production",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "SECRET_KEY": "s3cr3t",
    "DEBUG": "false",
}


def test_trim_by_keys_removes_exact_keys():
    result = trim_by_keys(SAMPLE, ["DEBUG", "SECRET_KEY"])
    assert "DEBUG" not in result
    assert "SECRET_KEY" not in result
    assert "APP_NAME" in result


def test_trim_by_keys_ignores_missing_keys():
    result = trim_by_keys(SAMPLE, ["NONEXISTENT"])
    assert result == SAMPLE


def test_trim_by_keys_does_not_mutate_original():
    original = dict(SAMPLE)
    trim_by_keys(original, ["APP_NAME"])
    assert original == SAMPLE


def test_trim_by_prefix_removes_matching():
    result = trim_by_prefix(SAMPLE, "DB_")
    assert "DB_HOST" not in result
    assert "DB_PORT" not in result
    assert "APP_NAME" in result


def test_trim_by_prefix_no_match_returns_full():
    result = trim_by_prefix(SAMPLE, "XYZ_")
    assert result == SAMPLE


def test_trim_by_pattern_glob():
    result = trim_by_pattern(SAMPLE, "APP_*")
    assert "APP_NAME" not in result
    assert "APP_ENV" not in result
    assert "DB_HOST" in result


def test_trim_by_pattern_no_match_returns_full():
    result = trim_by_pattern(SAMPLE, "NOTHING_*")
    assert result == SAMPLE


def test_trim_snapshot_keys_only():
    result = trim_snapshot(SAMPLE, keys=["DEBUG"])
    assert "DEBUG" not in result
    assert len(result) == len(SAMPLE) - 1


def test_trim_snapshot_combined_operations():
    result = trim_snapshot(SAMPLE, keys=["DEBUG"], prefix="APP_", pattern="SECRET_*")
    for key in ("DEBUG", "APP_NAME", "APP_ENV", "SECRET_KEY"):
        assert key not in result
    assert "DB_HOST" in result


def test_trim_snapshot_no_criteria_raises():
    with pytest.raises(TrimError):
        trim_snapshot(SAMPLE)


def test_trim_file_creates_dest(tmp_path):
    src = tmp_path / "snap.json"
    src.write_text(json.dumps(SAMPLE))
    dest = tmp_path / "trimmed.json"
    returned = trim_file(src, dest, keys=["DEBUG"])
    assert returned == dest
    assert dest.exists()


def test_trim_file_content_is_correct(tmp_path):
    src = tmp_path / "snap.json"
    src.write_text(json.dumps(SAMPLE))
    dest = tmp_path / "trimmed.json"
    trim_file(src, dest, prefix="DB_")
    result = json.loads(dest.read_text())
    assert "DB_HOST" not in result
    assert "DB_PORT" not in result
    assert "APP_NAME" in result
