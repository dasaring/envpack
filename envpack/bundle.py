"""Bundle multiple snapshots into a single archive file."""

import json
import zipfile
import os
from pathlib import Path
from typing import List, Dict, Optional

from envpack.snapshot import load


class BundleError(Exception):
    pass


def create_bundle(snapshot_paths: List[str], bundle_path: str, label: Optional[str] = None) -> Dict:
    """Pack multiple snapshot files into a zip bundle.

    Returns a manifest dict describing the bundle.
    """
    if not snapshot_paths:
        raise BundleError("Cannot create a bundle with no snapshots.")

    manifest = {
        "label": label,
        "snapshots": [],
    }

    with zipfile.ZipFile(bundle_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in snapshot_paths:
            p = Path(path)
            if not p.exists():
                raise BundleError(f"Snapshot file not found: {path}")
            zf.write(path, arcname=p.name)
            manifest["snapshots"].append(p.name)

        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    return manifest


def extract_bundle(bundle_path: str, dest_dir: str) -> Dict:
    """Extract all snapshots from a bundle into dest_dir.

    Returns the manifest dict.
    """
    if not os.path.exists(bundle_path):
        raise BundleError(f"Bundle not found: {bundle_path}")

    os.makedirs(dest_dir, exist_ok=True)

    with zipfile.ZipFile(bundle_path, "r") as zf:
        names = zf.namelist()
        if "manifest.json" not in names:
            raise BundleError("Bundle is missing manifest.json — may be corrupt.")

        manifest = json.loads(zf.read("manifest.json"))
        for name in names:
            if name == "manifest.json":
                continue
            zf.extract(name, dest_dir)

    return manifest


def list_bundle(bundle_path: str) -> Dict:
    """Return the manifest of a bundle without extracting it."""
    if not os.path.exists(bundle_path):
        raise BundleError(f"Bundle not found: {bundle_path}")

    with zipfile.ZipFile(bundle_path, "r") as zf:
        if "manifest.json" not in zf.namelist():
            raise BundleError("Bundle is missing manifest.json — may be corrupt.")
        return json.loads(zf.read("manifest.json"))
