"""Optional encryption support for envpack snapshots using Fernet symmetric encryption."""

import base64
import hashlib
import json
import os
from typing import Dict

try:
    from cryptography.fernet import Fernet, InvalidToken
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


def _require_cryptography() -> None:
    if not HAS_CRYPTOGRAPHY:
        raise RuntimeError(
            "cryptography package is required for encryption support. "
            "Install it with: pip install cryptography"
        )


def derive_key(passphrase: str) -> bytes:
    """Derive a Fernet-compatible key from a passphrase using SHA-256."""
    _require_cryptography()
    digest = hashlib.sha256(passphrase.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_snapshot(snapshot: Dict[str, str], passphrase: str) -> bytes:
    """Encrypt a snapshot dict to bytes using the given passphrase."""
    _require_cryptography()
    from cryptography.fernet import Fernet
    key = derive_key(passphrase)
    f = Fernet(key)
    plaintext = json.dumps(snapshot).encode()
    return f.encrypt(plaintext)


def decrypt_snapshot(token: bytes, passphrase: str) -> Dict[str, str]:
    """Decrypt bytes back to a snapshot dict using the given passphrase."""
    _require_cryptography()
    from cryptography.fernet import Fernet, InvalidToken
    key = derive_key(passphrase)
    f = Fernet(key)
    try:
        plaintext = f.decrypt(token)
    except InvalidToken:
        raise ValueError("Decryption failed: invalid passphrase or corrupted data.")
    return json.loads(plaintext.decode())


def save_encrypted(snapshot: Dict[str, str], path: str, passphrase: str) -> None:
    """Encrypt and write a snapshot to a .enc file."""
    token = encrypt_snapshot(snapshot, passphrase)
    with open(path, "wb") as fh:
        fh.write(token)


def load_encrypted(path: str, passphrase: str) -> Dict[str, str]:
    """Read and decrypt a snapshot from a .enc file."""
    with open(path, "rb") as fh:
        token = fh.read()
    return decrypt_snapshot(token, passphrase)
