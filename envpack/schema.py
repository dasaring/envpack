"""Schema validation for envpack snapshots.

Allows defining expected keys, types (string patterns), and whether
keys are optional or required, then validating a snapshot against it.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SchemaField:
    required: bool = True
    pattern: Optional[str] = None  # regex pattern the value must match
    description: str = ""


@dataclass
class SchemaResult:
    missing_required: List[str] = field(default_factory=list)
    pattern_failures: Dict[str, str] = field(default_factory=dict)  # key -> value
    unexpected_keys: List[str] = field(default_factory=list)

    def is_valid(self) -> bool:
        return (
            not self.missing_required
            and not self.pattern_failures
            and not self.unexpected_keys
        )

    def summary(self) -> str:
        lines = []
        if self.missing_required:
            lines.append("Missing required keys: " + ", ".join(self.missing_required))
        for key, value in self.pattern_failures.items():
            lines.append(f"Pattern mismatch for '{key}': {value!r}")
        if self.unexpected_keys:
            lines.append("Unexpected keys: " + ", ".join(self.unexpected_keys))
        return "\n".join(lines) if lines else "Schema valid."


def load_schema(path: str | Path) -> Dict[str, SchemaField]:
    """Load a schema definition from a JSON file."""
    data = json.loads(Path(path).read_text())
    schema: Dict[str, SchemaField] = {}
    for key, spec in data.items():
        schema[key] = SchemaField(
            required=spec.get("required", True),
            pattern=spec.get("pattern"),
            description=spec.get("description", ""),
        )
    return schema


def save_schema(schema: Dict[str, SchemaField], path: str | Path) -> None:
    """Persist a schema definition to a JSON file."""
    data = {
        key: {
            "required": f.required,
            "pattern": f.pattern,
            "description": f.description,
        }
        for key, f in schema.items()
    }
    Path(path).write_text(json.dumps(data, indent=2))


def validate_against_schema(
    snapshot: Dict[str, str],
    schema: Dict[str, SchemaField],
    allow_extra: bool = True,
) -> SchemaResult:
    """Validate a snapshot dict against a schema."""
    result = SchemaResult()

    for key, field_def in schema.items():
        if key not in snapshot:
            if field_def.required:
                result.missing_required.append(key)
        else:
            if field_def.pattern and not re.fullmatch(field_def.pattern, snapshot[key]):
                result.pattern_failures[key] = snapshot[key]

    if not allow_extra:
        for key in snapshot:
            if key not in schema:
                result.unexpected_keys.append(key)

    return result
