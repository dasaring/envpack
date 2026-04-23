"""Tests for envpack.signature."""

import json
import pytest
from pathlib import Path

from envpack.signature import (
    SIGNATURE_KEY,
    sign_snapshot,
    verify_snapshot,
    sign_file,
    verify_file,
    strip_signature,
)


SECRET = "supersecret"
SAMPLE = {"HOME": "/home/user", "PATH": "/usr/bin", "PORT": "8080"}


def test_sign_snapshot_adds_signature_key():
    signed = sign_snapshot(SAMPLE, SECRET)
    assert SIGNATURE_KEY in signed


def test_sign_snapshot_does_not_mutate_original():
    original = dict(SAMPLE)
    sign_snapshot(SAMPLE, SECRET)
    assert SAMPLE == original


def test_sign_snapshot_signature_is_hex_string():
    signed = sign_snapshot(SAMPLE, SECRET)
    sig = signed[SIGNATURE_KEY]
    assert isinstance(sig, str)
    assert len(sig) == 64  # SHA-256 hex digest


def test_verify_snapshot_returns_true_for_valid():
    signed = sign_snapshot(SAMPLE, SECRET)
    assert verify_snapshot(signed, SECRET) is True


def test_verify_snapshot_returns_false_for_wrong_secret():
    signed = sign_snapshot(SAMPLE, SECRET)
    assert verify_snapshot(signed, "wrongsecret") is False


def test_verify_snapshot_returns_false_when_no_signature():
    assert verify_snapshot(SAMPLE, SECRET) is False


def test_verify_snapshot_returns_false_when_data_tampered():
    signed = sign_snapshot(SAMPLE, SECRET)
    signed["INJECTED"] = "evil"
    assert verify_snapshot(signed, SECRET) is False


def test_sign_is_deterministic():
    sig1 = sign_snapshot(SAMPLE, SECRET)[SIGNATURE_KEY]
    sig2 = sign_snapshot(SAMPLE, SECRET)[SIGNATURE_KEY]
    assert sig1 == sig2


def test_different_secrets_produce_different_signatures():
    sig1 = sign_snapshot(SAMPLE, "secret1")[SIGNATURE_KEY]
    sig2 = sign_snapshot(SAMPLE, "secret2")[SIGNATURE_KEY]
    assert sig1 != sig2


def test_strip_signature_removes_key():
    signed = sign_snapshot(SAMPLE, SECRET)
    stripped = strip_signature(signed)
    assert SIGNATURE_KEY not in stripped


def test_strip_signature_preserves_other_keys():
    signed = sign_snapshot(SAMPLE, SECRET)
    stripped = strip_signature(signed)
    assert stripped == SAMPLE


def test_sign_file_and_verify_file(tmp_path):
    snap_path = tmp_path / "snap.json"
    snap_path.write_text(json.dumps(SAMPLE))
    sign_file(snap_path, SECRET)
    assert verify_file(snap_path, SECRET) is True


def test_sign_file_embeds_signature_in_file(tmp_path):
    snap_path = tmp_path / "snap.json"
    snap_path.write_text(json.dumps(SAMPLE))
    sign_file(snap_path, SECRET)
    data = json.loads(snap_path.read_text())
    assert SIGNATURE_KEY in data


def test_verify_file_returns_false_for_unsigned_file(tmp_path):
    snap_path = tmp_path / "snap.json"
    snap_path.write_text(json.dumps(SAMPLE))
    assert verify_file(snap_path, SECRET) is False
