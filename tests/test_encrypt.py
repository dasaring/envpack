"""Tests for envpack.encrypt module."""

import json
import os
import pytest

pytest.importorskip("cryptography", reason="cryptography package not installed")

from envpack.encrypt import (
    derive_key,
    encrypt_snapshot,
    decrypt_snapshot,
    save_encrypted,
    load_encrypted,
)

SAMPLE = {"API_KEY": "secret123", "DEBUG": "true", "PORT": "8080"}
PASS = "hunter2"


def test_derive_key_is_deterministic():
    assert derive_key(PASS) == derive_key(PASS)


def test_derive_key_differs_for_different_passphrases():
    assert derive_key(PASS) != derive_key("other")


def test_derive_key_length():
    # Fernet keys are 32 bytes base64-encoded = 44 chars
    key = derive_key(PASS)
    import base64
    assert len(base64.urlsafe_b64decode(key)) == 32


def test_encrypt_returns_bytes():
    token = encrypt_snapshot(SAMPLE, PASS)
    assert isinstance(token, bytes)


def test_encrypt_decrypt_roundtrip():
    token = encrypt_snapshot(SAMPLE, PASS)
    result = decrypt_snapshot(token, PASS)
    assert result == SAMPLE


def test_decrypt_wrong_passphrase_raises():
    token = encrypt_snapshot(SAMPLE, PASS)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_snapshot(token, "wrongpass")


def test_decrypt_corrupted_data_raises():
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_snapshot(b"notvalidtoken", PASS)


def test_save_and_load_encrypted(tmp_path):
    enc_file = str(tmp_path / "snap.enc")
    save_encrypted(SAMPLE, enc_file, PASS)
    assert os.path.exists(enc_file)
    loaded = load_encrypted(enc_file, PASS)
    assert loaded == SAMPLE


def test_save_encrypted_file_is_not_plaintext(tmp_path):
    enc_file = str(tmp_path / "snap.enc")
    save_encrypted(SAMPLE, enc_file, PASS)
    raw = open(enc_file, "rb").read()
    assert b"API_KEY" not in raw
    assert b"secret123" not in raw


def test_no_cryptography_raises(monkeypatch):
    import envpack.encrypt as enc_mod
    monkeypatch.setattr(enc_mod, "HAS_CRYPTOGRAPHY", False)
    with pytest.raises(RuntimeError, match="cryptography package"):
        enc_mod._require_cryptography()
