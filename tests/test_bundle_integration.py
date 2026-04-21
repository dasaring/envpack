"""Integration tests: full create → list → extract → verify cycle."""

import json
import os
import pytest

from envpack.bundle import create_bundle, extract_bundle, list_bundle


@pytest.fixture()
def snapshot_path(tmp_path):
    """Write a real snapshot file and return its path."""
    snap = {"DATABASE_URL": "postgres://localhost/dev", "SECRET_KEY": "abc123"}
    p = tmp_path / "dev.json"
    p.write_text(json.dumps(snap))
    return str(p)


@pytest.fixture()
def snapshot_path_2(tmp_path):
    snap = {"API_KEY": "key-xyz", "TIMEOUT": "30"}
    p = tmp_path / "staging.json"
    p.write_text(json.dumps(snap))
    return str(p)


def test_full_lifecycle(snapshot_path, snapshot_path_2, tmp_path):
    """Create a bundle, list it, extract it, verify file contents."""
    bundle = str(tmp_path / "release.zip")

    # Create
    manifest = create_bundle([snapshot_path, snapshot_path_2], bundle, label="release-2024")
    assert os.path.exists(bundle)
    assert len(manifest["snapshots"]) == 2

    # List
    listed = list_bundle(bundle)
    assert listed["label"] == "release-2024"
    assert set(listed["snapshots"]) == {"dev.json", "staging.json"}

    # Extract
    dest = str(tmp_path / "restored")
    extract_bundle(bundle, dest)

    # Verify contents
    dev_data = json.loads(open(os.path.join(dest, "dev.json")).read())
    assert dev_data["DATABASE_URL"] == "postgres://localhost/dev"

    staging_data = json.loads(open(os.path.join(dest, "staging.json")).read())
    assert staging_data["API_KEY"] == "key-xyz"


def test_single_snapshot_bundle(snapshot_path, tmp_path):
    """A bundle with a single snapshot works end-to-end."""
    bundle = str(tmp_path / "single.zip")
    create_bundle([snapshot_path], bundle)
    manifest = list_bundle(bundle)
    assert manifest["snapshots"] == ["dev.json"]

    dest = str(tmp_path / "out")
    extract_bundle(bundle, dest)
    assert os.path.exists(os.path.join(dest, "dev.json"))
