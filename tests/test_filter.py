"""Tests for envpack.filter."""

import pytest
from envpack.filter import (
    exclude_keys,
    filter_by_keys,
    filter_by_prefix,
    filter_by_value_pattern,
    filter_snapshot,
)

SAMPLE: dict = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.local",
    "DB_PASSWORD": "s3cr3t",
    "DEBUG": "true",
    "SECRET_KEY": "abc123",
}


def test_filter_by_keys_exact_match():
    result = filter_by_keys(SAMPLE, ["DEBUG"])
    assert result == {"DEBUG": "true"}


def test_filter_by_keys_glob():
    result = filter_by_keys(SAMPLE, ["APP_*"])
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_filter_by_keys_multiple_patterns():
    result = filter_by_keys(SAMPLE, ["APP_*", "DB_HOST"])
    assert set(result.keys()) == {"APP_HOST", "APP_PORT", "DB_HOST"}


def test_filter_by_keys_no_match_returns_empty():
    result = filter_by_keys(SAMPLE, ["NONEXISTENT_*"])
    assert result == {}


def test_filter_by_prefix():
    result = filter_by_prefix(SAMPLE, "DB_")
    assert set(result.keys()) == {"DB_HOST", "DB_PASSWORD"}


def test_filter_by_prefix_no_match():
    result = filter_by_prefix(SAMPLE, "XYZ_")
    assert result == {}


def test_filter_by_value_pattern_simple():
    result = filter_by_value_pattern(SAMPLE, r"\d+")
    assert "APP_PORT" in result
    assert "APP_HOST" not in result


def test_filter_by_value_pattern_no_match():
    result = filter_by_value_pattern(SAMPLE, r"^ZZZZ")
    assert result == {}


def test_exclude_keys_glob():
    result = exclude_keys(SAMPLE, ["DB_*"])
    assert "DB_HOST" not in result
    assert "DB_PASSWORD" not in result
    assert "APP_HOST" in result


def test_exclude_keys_exact():
    result = exclude_keys(SAMPLE, ["DEBUG"])
    assert "DEBUG" not in result
    assert len(result) == len(SAMPLE) - 1


def test_filter_snapshot_include_only():
    result = filter_snapshot(SAMPLE, include=["APP_*"])
    assert set(result.keys()) == {"APP_HOST", "APP_PORT"}


def test_filter_snapshot_exclude_only():
    result = filter_snapshot(SAMPLE, exclude=["SECRET_*", "DB_PASSWORD"])
    assert "SECRET_KEY" not in result
    assert "DB_PASSWORD" not in result


def test_filter_snapshot_prefix():
    result = filter_snapshot(SAMPLE, prefix="APP_")
    assert all(k.startswith("APP_") for k in result)


def test_filter_snapshot_combined():
    result = filter_snapshot(SAMPLE, include=["APP_*", "DB_*"], exclude=["DB_PASSWORD"])
    assert "APP_HOST" in result
    assert "DB_HOST" in result
    assert "DB_PASSWORD" not in result


def test_filter_snapshot_does_not_mutate_original():
    original = dict(SAMPLE)
    filter_snapshot(SAMPLE, include=["APP_*"], exclude=["APP_PORT"])
    assert SAMPLE == original
