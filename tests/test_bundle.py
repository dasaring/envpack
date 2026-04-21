"""Tests for envpack.bundle."""

import json
import os
import zipfile
import pytest

from envpack.bundle import create_bundle, extract_bundle, list_bundle, BundleError


@pytest.fixture()
def snap_dir(tmp_path):
    """Create a temp dir with two snapshot JSON files."""
    a = tmp_path / "snap_a.json"
    b = tmp_path / "snap_b.json"
    a.write_text(json.dumps({"FOO": "bar"}))
    b.write_text(json.dumps({"BAZ": "qux"}))
    return tmp_path, str(a), str(b)


def test_create_bundle_produces_zip(snap_dir, tmp_path):
    _, a, b = snap_dir
    out = str(tmp_path / "env.bundle.zip")
    create_bundle([a, b], out)
    assert os.path.exists(out)
    assert zipfile.is_zipfile(out)


def test_create_bundle_contains_manifest(snap_dir, tmp_path):
    _, a, b = snap_dir
    out = str(tmp_path / "env.bundle.zip")
    create_bundle([a, b], out)
    with zipfile.ZipFile(out) as zf:
        assert "manifest.json" in zf.namelist()


def test_create_bundle_manifest_has_snapshots(snap_dir, tmp_path):
    _, a, b = snap_dir
    out = str(tmp_path / "env.bundle.zip")
    manifest = create_bundle([a, b], out)
    assert "snap_a.json" in manifest["snapshots"]
    assert "snap_b.json" in manifest["snapshots"]


def test_create_bundle_with_label(snap_dir, tmp_path):
    _, a, _ = snap_dir
    out = str(tmp_path / "labeled.zip")
    manifest = create_bundle([a], out, label="my-label")
    assert manifest["label"] == "my-label"


def test_create_bundle_empty_list_raises(tmp_path):
    out = str(tmp_path / "empty.zip")
    with pytest.raises(BundleError, match="no snapshots"):
        create_bundle([], out)


def test_create_bundle_missing_file_raises(tmp_path):
    out = str(tmp_path / "bad.zip")
    with pytest.raises(BundleError, match="not found"):
        create_bundle(["/nonexistent/snap.json"], out)


def test_extract_bundle_creates_files(snap_dir, tmp_path):
    _, a, b = snap_dir
    bundle = str(tmp_path / "env.zip")
    create_bundle([a, b], bundle)
    dest = str(tmp_path / "extracted")
    manifest = extract_bundle(bundle, dest)
    assert os.path.exists(os.path.join(dest, "snap_a.json"))
    assert os.path.exists(os.path.join(dest, "snap_b.json"))
    assert set(manifest["snapshots"]) == {"snap_a.json", "snap_b.json"}


def test_extract_bundle_missing_raises(tmp_path):
    with pytest.raises(BundleError, match="not found"):
        extract_bundle(str(tmp_path / "ghost.zip"), str(tmp_path / "out"))


def test_list_bundle_returns_manifest(snap_dir, tmp_path):
    _, a, b = snap_dir
    bundle = str(tmp_path / "env.zip")
    create_bundle([a, b], bundle, label="test-label")
    manifest = list_bundle(bundle)
    assert manifest["label"] == "test-label"
    assert "snap_a.json" in manifest["snapshots"]


def test_list_bundle_missing_raises(tmp_path):
    with pytest.raises(BundleError, match="not found"):
        list_bundle(str(tmp_path / "ghost.zip"))
