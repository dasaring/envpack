"""Tests for envpack.snapshot module."""

import json
import os
from pathlib import Path

import pytest

from envpack.snapshot import capture, load, save


def test_capture_all_env_vars():
    os.environ["ENVPACK_TEST_VAR"] = "hello"
    snapshot = capture("test")
    assert snapshot["name"] == "test"
    assert "created_at" in snapshot
    assert snapshot["variables"]["ENVPACK_TEST_VAR"] == "hello"


def test_capture_specific_keys():
    os.environ["ENVPACK_A"] = "1"
    os.environ["ENVPACK_B"] = "2"
    snapshot = capture("selective", keys=["ENVPACK_A", "MISSING_KEY"])
    assert "ENVPACK_A" in snapshot["variables"]
    assert "ENVPACK_B" not in snapshot["variables"]
    assert "MISSING_KEY" not in snapshot["variables"]


def test_save_creates_file(tmp_path):
    snapshot = capture("my snapshot")
    path = save(snapshot, directory=tmp_path)
    assert path.exists()
    assert path.name == "my_snapshot.json"


def test_save_content_is_valid_json(tmp_path):
    snapshot = capture("json_test")
    path = save(snapshot, directory=tmp_path)
    data = json.loads(path.read_text())
    assert data["name"] == "json_test"


def test_load_returns_snapshot(tmp_path):
    snapshot = capture("load_test")
    path = save(snapshot, directory=tmp_path)
    loaded = load(path)
    assert loaded["name"] == "load_test"
    assert "variables" in loaded


def test_load_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load(tmp_path / "nonexistent.json")


def test_load_invalid_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not json", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load(bad_file)


def test_load_missing_required_key(tmp_path):
    incomplete = tmp_path / "incomplete.json"
    incomplete.write_text(json.dumps({"name": "x"}), encoding="utf-8")
    with pytest.raises(ValueError, match="missing required key"):
        load(incomplete)
