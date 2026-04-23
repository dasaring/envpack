"""Integration tests: label -> snapshot file on disk."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.label import add_label, list_labels, remove_label, resolve_label


@pytest.fixture()
def snapshot_path(tmp_path: Path) -> Path:
    snap = tmp_path / "snap.json"
    snap.write_text(json.dumps({"HOME": "/home/user", "USER": "alice"}))
    return snap


@pytest.fixture()
def label_file(tmp_path: Path) -> Path:
    return tmp_path / "labels.json"


def test_label_points_to_existing_snapshot(snapshot_path, label_file):
    add_label("my-snap", str(snapshot_path), label_file)
    resolved = resolve_label("my-snap", label_file)
    assert resolved is not None
    p = Path(resolved)
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["USER"] == "alice"


def test_label_lifecycle(snapshot_path, label_file):
    add_label("v1", str(snapshot_path), label_file)
    assert resolve_label("v1", label_file) == str(snapshot_path)
    assert len(list_labels(label_file)) == 1

    remove_label("v1", label_file)
    assert resolve_label("v1", label_file) is None
    assert list_labels(label_file) == []


def test_multiple_labels_independent(snapshot_path, label_file, tmp_path):
    snap2 = tmp_path / "snap2.json"
    snap2.write_text(json.dumps({"ENV": "prod"}))

    add_label("dev", str(snapshot_path), label_file)
    add_label("prod", str(snap2), label_file)

    assert resolve_label("dev", label_file) == str(snapshot_path)
    assert resolve_label("prod", label_file) == str(snap2)

    remove_label("dev", label_file)
    assert resolve_label("prod", label_file) == str(snap2)
