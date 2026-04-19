"""Validate snapshot contents against a schema/rules."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = []
        if self.valid:
            lines.append("Snapshot is valid.")
        else:
            lines.append("Snapshot is INVALID.")
        for e in self.errors:
            lines.append(f"  ERROR: {e}")
        for w in self.warnings:
            lines.append(f"  WARN:  {w}")
        return "\n".join(lines)


def _is_valid_key(key: str) -> bool:
    return bool(re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', key))


def validate_snapshot(
    snapshot: Dict[str, str],
    required_keys: Optional[List[str]] = None,
    forbidden_keys: Optional[List[str]] = None,
    max_value_length: int = 4096,
) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    for key in snapshot:
        if not _is_valid_key(key):
            errors.append(f"Invalid key name: {key!r}")
        value = snapshot[key]
        if not isinstance(value, str):
            errors.append(f"Value for {key!r} is not a string.")
        elif len(value) > max_value_length:
            warnings.append(f"Value for {key!r} exceeds {max_value_length} chars.")

    for key in (required_keys or []):
        if key not in snapshot:
            errors.append(f"Required key missing: {key!r}")

    for key in (forbidden_keys or []):
        if key in snapshot:
            errors.append(f"Forbidden key present: {key!r}")

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
