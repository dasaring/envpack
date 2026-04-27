"""Transform snapshot key/value pairs using built-in or custom operations."""

from __future__ import annotations

import re
from typing import Callable, Dict, Optional


class TransformError(Exception):
    """Raised when a transform operation fails."""


# Built-in value transformers
_BUILTIN_TRANSFORMS: Dict[str, Callable[[str], str]] = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
    "reverse": lambda v: v[::-1],
}


def transform_values(
    snapshot: Dict[str, str],
    operation: str,
    keys: Optional[list] = None,
) -> Dict[str, str]:
    """Apply a named operation to snapshot values.

    Args:
        snapshot: Source snapshot dict.
        operation: Name of a built-in transform (upper, lower, strip, reverse).
        keys: Optional list of keys to restrict the transform to.
              If None, all keys are transformed.

    Returns:
        New snapshot with transformed values; original is not mutated.

    Raises:
        TransformError: If *operation* is not recognised.
    """
    if operation not in _BUILTIN_TRANSFORMS:
        raise TransformError(
            f"Unknown transform operation '{operation}'. "
            f"Available: {sorted(_BUILTIN_TRANSFORMS)}"
        )
    fn = _BUILTIN_TRANSFORMS[operation]
    target_keys = set(keys) if keys is not None else None
    return {
        k: (fn(v) if (target_keys is None or k in target_keys) else v)
        for k, v in snapshot.items()
    }


def rename_keys(
    snapshot: Dict[str, str],
    mapping: Dict[str, str],
    ignore_missing: bool = True,
) -> Dict[str, str]:
    """Return a new snapshot with keys renamed according to *mapping*.

    Args:
        snapshot: Source snapshot dict.
        mapping: Old-name -> new-name pairs.
        ignore_missing: When True, silently skip keys in *mapping* that are
                        absent from *snapshot*.  When False, raise TransformError.

    Returns:
        New snapshot with renamed keys.
    """
    result: Dict[str, str] = {}
    for k, v in snapshot.items():
        if k in mapping:
            result[mapping[k]] = v
        else:
            result[k] = v
    if not ignore_missing:
        for old in mapping:
            if old not in snapshot:
                raise TransformError(f"Key '{old}' not found in snapshot.")
    return result


def apply_regex(
    snapshot: Dict[str, str],
    pattern: str,
    replacement: str,
    keys: Optional[list] = None,
) -> Dict[str, str]:
    """Apply a regex substitution to snapshot values.

    Args:
        snapshot: Source snapshot dict.
        pattern: Regular expression pattern.
        replacement: Replacement string (supports back-references).
        keys: Optional list of keys to restrict the transform to.

    Returns:
        New snapshot with substituted values.
    """
    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        raise TransformError(f"Invalid regex pattern: {exc}") from exc
    target_keys = set(keys) if keys is not None else None
    return {
        k: (re.sub(compiled, replacement, v) if (target_keys is None or k in target_keys) else v)
        for k, v in snapshot.items()
    }
