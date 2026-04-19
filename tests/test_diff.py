"""Tests for envpack.diff module."""

import pytest
from envpack.diff import diff_snapshots, DiffResult


BASE = {"HOME": "/home/user", "PATH": "/usr/bin", "LANG": "en_US"}


def test_no_differences():
    result = diff_snapshots(BASE, BASE.copy())
    assert result.is_empty()


def test_added_keys():
    after = {**BASE, "NEW_VAR": "hello"}
    result = diff_snapshots(BASE, after)
    assert result.added == {"NEW_VAR": "hello"}
    assert not result.removed
    assert not result.changed


def test_removed_keys():
    after = {k: v for k, v in BASE.items() if k != "LANG"}
    result = diff_snapshots(BASE, after)
    assert result.removed == {"LANG": "en_US"}
    assert not result.added
    assert not result.changed


def test_changed_keys():
    after = {**BASE, "PATH": "/usr/local/bin"}
    result = diff_snapshots(BASE, after)
    assert result.changed == {"PATH": ("/usr/bin", "/usr/local/bin")}
    assert not result.added
    assert not result.removed


def test_combined_diff():
    after = {"HOME": "/root", "NEW": "val"}
    result = diff_snapshots(BASE, after)
    assert "NEW" in result.added
    assert "PATH" in result.removed
    assert "LANG" in result.removed
    assert "HOME" in result.changed


def test_empty_before():
    result = diff_snapshots({}, BASE)
    assert result.added == BASE
    assert not result.removed
    assert not result.changed


def test_empty_after():
    result = diff_snapshots(BASE, {})
    assert result.removed == BASE
    assert not result.added
    assert not result.changed


def test_summary_no_diff():
    result = diff_snapshots(BASE, BASE)
    assert result.summary() == "(no differences)"


def test_summary_contains_markers():
    after = {**BASE, "NEW_VAR": "x", "PATH": "/changed"}
    after.pop("LANG")
    result = diff_snapshots(BASE, after)
    summary = result.summary()
    assert "+ NEW_VAR=x" in summary
    assert "- LANG=en_US" in summary
    assert "~ PATH" in summary
