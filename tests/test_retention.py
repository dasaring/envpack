"""Tests for envpack.retention."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envpack.retention import (
    apply_policy,
    get_policy,
    list_policies,
    remove_policy,
    set_policy,
)


@pytest.fixture
def pfile(tmp_path):
    return tmp_path / "retention.json"


def test_set_policy_max_count(pfile):
    entry = set_policy("ci", max_count=5, policy_file=pfile)
    assert entry["name"] == "ci"
    assert entry["max_count"] == 5
    assert "max_age_days" not in entry


def test_set_policy_max_age_days(pfile):
    entry = set_policy("weekly", max_age_days=7, policy_file=pfile)
    assert entry["max_age_days"] == 7


def test_set_policy_both(pfile):
    entry = set_policy("combo", max_count=10, max_age_days=30, policy_file=pfile)
    assert entry["max_count"] == 10
    assert entry["max_age_days"] == 30


def test_set_policy_no_constraints_raises(pfile):
    with pytest.raises(ValueError):
        set_policy("bad", policy_file=pfile)


def test_get_policy_returns_entry(pfile):
    set_policy("ci", max_count=3, policy_file=pfile)
    result = get_policy("ci", policy_file=pfile)
    assert result is not None
    assert result["max_count"] == 3


def test_get_policy_missing_returns_none(pfile):
    assert get_policy("ghost", policy_file=pfile) is None


def test_remove_policy_returns_true(pfile):
    set_policy("ci", max_count=5, policy_file=pfile)
    assert remove_policy("ci", policy_file=pfile) is True
    assert get_policy("ci", policy_file=pfile) is None


def test_remove_policy_missing_returns_false(pfile):
    assert remove_policy("nope", policy_file=pfile) is False


def test_list_policies_empty(pfile):
    assert list_policies(policy_file=pfile) == []


def test_list_policies_multiple(pfile):
    set_policy("a", max_count=1, policy_file=pfile)
    set_policy("b", max_age_days=2, policy_file=pfile)
    names = {p["name"] for p in list_policies(policy_file=pfile)}
    assert names == {"a", "b"}


def test_apply_policy_max_count_prunes_oldest(tmp_path, pfile):
    snaps = []
    for i in range(5):
        p = tmp_path / f"snap_{i}.json"
        p.write_text("{}")
        snaps.append(p)
    set_policy("ci", max_count=3, policy_file=pfile)
    to_prune = apply_policy("ci", snaps, policy_file=pfile)
    assert len(to_prune) == 2
    assert snaps[0] in to_prune
    assert snaps[1] in to_prune


def test_apply_policy_max_count_no_prune_needed(tmp_path, pfile):
    snaps = [tmp_path / f"snap_{i}.json" for i in range(2)]
    for p in snaps:
        p.write_text("{}")
    set_policy("ci", max_count=5, policy_file=pfile)
    assert apply_policy("ci", snaps, policy_file=pfile) == []


def test_apply_policy_max_age_prunes_old(tmp_path, pfile):
    old = tmp_path / "old.json"
    old.write_text("{}")
    old_time = time.time() - (10 * 86400)
    import os
    os.utime(old, (old_time, old_time))

    recent = tmp_path / "recent.json"
    recent.write_text("{}")

    set_policy("weekly", max_age_days=7, policy_file=pfile)
    to_prune = apply_policy("weekly", [old, recent], policy_file=pfile)
    assert old in to_prune
    assert recent not in to_prune


def test_apply_policy_unknown_raises(tmp_path, pfile):
    with pytest.raises(KeyError, match="not found"):
        apply_policy("ghost", [], policy_file=pfile)
