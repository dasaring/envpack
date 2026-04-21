"""Redact sensitive values from snapshots before display or export."""

from __future__ import annotations

import re
from typing import Dict, Iterable, Optional

_SENSITIVE_PATTERNS = [
    re.compile(r"(password|passwd|secret|token|api[_\-]?key|auth|credential|private[_\-]?key|access[_\-]?key)", re.IGNORECASE),
]

DEFAULT_MASK = "***REDACTED***"


def is_sensitive_key(key: str) -> bool:
    """Return True if the key name looks sensitive."""
    for pattern in _SENSITIVE_PATTERNS:
        if pattern.search(key):
            return True
    return False


def redact_snapshot(
    snapshot: Dict[str, str],
    *,
    extra_keys: Optional[Iterable[str]] = None,
    mask: str = DEFAULT_MASK,
    allow_keys: Optional[Iterable[str]] = None,
) -> Dict[str, str]:
    """Return a copy of *snapshot* with sensitive values replaced by *mask*.

    Args:
        snapshot:   The original key/value mapping.
        extra_keys: Additional key names (exact, case-insensitive) to redact.
        mask:       Replacement string for redacted values.
        allow_keys: Keys that should *not* be redacted even if they match.
    """
    forced: set[str] = {k.upper() for k in (extra_keys or [])}
    allowed: set[str] = {k.upper() for k in (allow_keys or [])}

    result: Dict[str, str] = {}
    for key, value in snapshot.items():
        upper = key.upper()
        if upper in allowed:
            result[key] = value
        elif upper in forced or is_sensitive_key(key):
            result[key] = mask
        else:
            result[key] = value
    return result


def redacted_keys(
    snapshot: Dict[str, str],
    *,
    extra_keys: Optional[Iterable[str]] = None,
    allow_keys: Optional[Iterable[str]] = None,
) -> list[str]:
    """Return a sorted list of keys that *would* be redacted."""
    forced: set[str] = {k.upper() for k in (extra_keys or [])}
    allowed: set[str] = {k.upper() for k in (allow_keys or [])}

    result = []
    for key in snapshot:
        upper = key.upper()
        if upper in allowed:
            continue
        if upper in forced or is_sensitive_key(key):
            result.append(key)
    return sorted(result)
