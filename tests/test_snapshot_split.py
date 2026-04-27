"""Tests for envpack.snapshot_split."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.snapshot_split import save_split, split_by_keys, split_by_prefix


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "AWS_KEY": "abc",
    "AWS_SECRET": "xyz",
    "APP_NAME": "envpack",
    "UNTAGGED": "value",
}


# ---------------------------------------------------------------------------
# split_by_prefix
# ---------------------------------------------------------------------------

def test_split_by_prefix_groups_correctly():
    parts = split_by_prefix(SAMPLE, ["DB_", "AWS_"])
    assert set(parts["DB_"].keys()) == {"DB_HOST", "DB_PORT"}
    assert set(parts["AWS_"].keys()) == {"AWS_KEY", "AWS_SECRET"}


def test_split_by_prefix_other_bucket():
    parts = split_by_prefix(SAMPLE, ["DB_", "AWS_"])
    assert "APP_NAME" in parts["_other"]
    assert "UNTAGGED" in parts["_other"]


def test_split_by_prefix_strip_prefix():
    parts = split_by_prefix(SAMPLE, ["DB_"], strip_prefix=True)
    assert "HOST" in parts["DB_"]
    assert "PORT" in parts["DB_"]


def test_split_by_prefix_no_match_all_in_other():
    parts = split_by_prefix(SAMPLE, ["MISSING_"])
    assert parts["MISSING_"] == {}
    assert len(parts["_other"]) == len(SAMPLE)


def test_split_by_prefix_empty_snapshot():
    parts = split_by_prefix({}, ["DB_"])
    assert parts["DB_"] == {}
    assert parts["_other"] == {}


# ---------------------------------------------------------------------------
# split_by_keys
# ---------------------------------------------------------------------------

def test_split_by_keys_assigns_correctly():
    groups = {"db": ["DB_HOST", "DB_PORT"], "aws": ["AWS_KEY", "AWS_SECRET"]}
    parts = split_by_keys(SAMPLE, groups)
    assert parts["db"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert parts["aws"] == {"AWS_KEY": "abc", "AWS_SECRET": "xyz"}


def test_split_by_keys_missing_keys_ignored():
    groups = {"db": ["DB_HOST", "DB_DOES_NOT_EXIST"]}
    parts = split_by_keys(SAMPLE, groups)
    assert list(parts["db"].keys()) == ["DB_HOST"]


def test_split_by_keys_unassigned_go_to_other():
    groups = {"db": ["DB_HOST", "DB_PORT"]}
    parts = split_by_keys(SAMPLE, groups)
    assert "AWS_KEY" in parts["_other"]
    assert "UNTAGGED" in parts["_other"]


def test_split_by_keys_empty_groups():
    parts = split_by_keys(SAMPLE, {})
    assert parts["_other"] == SAMPLE


# ---------------------------------------------------------------------------
# save_split
# ---------------------------------------------------------------------------

def test_save_split_creates_files(tmp_path):
    parts = {"db": {"DB_HOST": "localhost"}, "aws": {"AWS_KEY": "abc"}}
    written = save_split(parts, tmp_path, base_name="env")
    assert tmp_path.joinpath("env_db.json").exists()
    assert tmp_path.joinpath("env_aws.json").exists()


def test_save_split_skips_empty_by_default(tmp_path):
    parts = {"db": {"DB_HOST": "localhost"}, "empty": {}}
    written = save_split(parts, tmp_path, base_name="env")
    assert "empty" not in written
    assert not tmp_path.joinpath("env_empty.json").exists()


def test_save_split_keep_empty_writes_file(tmp_path):
    parts = {"db": {}, "aws": {"AWS_KEY": "abc"}}
    written = save_split(parts, tmp_path, base_name="env", skip_empty=False)
    assert "db" in written
    assert tmp_path.joinpath("env_db.json").exists()


def test_save_split_content_is_valid_json(tmp_path):
    parts = {"db": {"DB_HOST": "localhost"}}
    written = save_split(parts, tmp_path, base_name="env")
    data = json.loads(written["db"].read_text())
    assert data == {"DB_HOST": "localhost"}


def test_save_split_creates_output_dir(tmp_path):
    nested = tmp_path / "a" / "b"
    parts = {"x": {"K": "v"}}
    save_split(parts, nested, base_name="env")
    assert nested.exists()
