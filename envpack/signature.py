"""Snapshot signing and verification using HMAC-SHA256."""

import hashlib
import hmac
import json
from pathlib import Path
from typing import Union


SIGNATURE_KEY = "__envpack_signature__"


def _canonical_bytes(snapshot: dict) -> bytes:
    """Produce a stable, canonical JSON representation of a snapshot (excluding signature)."""
    clean = {k: v for k, v in snapshot.items() if k != SIGNATURE_KEY}
    return json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()


def sign_snapshot(snapshot: dict, secret: str) -> dict:
    """Return a copy of the snapshot with an HMAC-SHA256 signature embedded."""
    payload = _canonical_bytes(snapshot)
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    signed = dict(snapshot)
    signed[SIGNATURE_KEY] = sig
    return signed


def verify_snapshot(snapshot: dict, secret: str) -> bool:
    """Verify the embedded signature of a snapshot. Returns True if valid."""
    expected_sig = snapshot.get(SIGNATURE_KEY)
    if expected_sig is None:
        return False
    payload = _canonical_bytes(snapshot)
    actual_sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_sig, actual_sig)


def sign_file(path: Union[str, Path], secret: str) -> Path:
    """Load a snapshot JSON file, embed a signature, and overwrite the file."""
    path = Path(path)
    snapshot = json.loads(path.read_text())
    signed = sign_snapshot(snapshot, secret)
    path.write_text(json.dumps(signed, indent=2))
    return path


def verify_file(path: Union[str, Path], secret: str) -> bool:
    """Load a snapshot JSON file and verify its embedded signature."""
    path = Path(path)
    snapshot = json.loads(path.read_text())
    return verify_snapshot(snapshot, secret)


def strip_signature(snapshot: dict) -> dict:
    """Return a copy of the snapshot with the signature field removed."""
    return {k: v for k, v in snapshot.items() if k != SIGNATURE_KEY}
