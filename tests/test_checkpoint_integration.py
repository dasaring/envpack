"""Integration tests: checkpoints referencing real snapshot files."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.checkpoint import create_checkpoint, delete_checkpoint, get_checkpoint
from envpack.snapshot import save


@pytest.fixture()
def snapshot_path(tmp_path: Path) -> Path:
    snap = {"APP_ENV": "production", "DB_HOST": "db.example.com"}
    p = tmp_path / "snap.json"
    save(snap, str(p))
    return p


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "checkpoints.json"


def test_checkpoint_references_existing_snapshot(snapshot_path: Path, store: Path) -> None:
    entry = create_checkpoint("prod", str(snapshot_path), store=store)
    ref = Path(entry["snapshot"])
    assert ref.exists()
    data = json.loads(ref.read_text())
    assert data["APP_ENV"] == "production"


def test_checkpoint_lifecycle(snapshot_path: Path, store: Path) -> None:
    create_checkpoint("prod", str(snapshot_path), description="stable", store=store)
    entry = get_checkpoint("prod", store=store)
    assert entry is not None
    assert entry["description"] == "stable"

    deleted = delete_checkpoint("prod", store=store)
    assert deleted is True
    assert get_checkpoint("prod", store=store) is None


def test_multiple_checkpoints_independent(tmp_path: Path, store: Path) -> None:
    for name in ("alpha", "beta"):
        p = tmp_path / f"{name}.json"
        save({"STAGE": name}, str(p))
        create_checkpoint(name, str(p), store=store)

    alpha = get_checkpoint("alpha", store=store)
    beta = get_checkpoint("beta", store=store)
    assert alpha is not None and beta is not None
    assert alpha["snapshot"] != beta["snapshot"]
