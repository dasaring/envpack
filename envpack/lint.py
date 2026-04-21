"""Lint snapshots for common issues and best practices."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Keys that should never appear in snapshots
SENSITIVE_PATTERNS = [
    re.compile(r"(password|passwd|secret|token|api_key|apikey|private_key)", re.IGNORECASE),
]

# Keys that look like they might have placeholder values
PLACEHOLDER_PATTERN = re.compile(r"^(CHANGE_ME|TODO|PLACEHOLDER|YOUR_.+|<.+>)$", re.IGNORECASE)

# Recommended max length for a single env var value
MAX_VALUE_LENGTH = 4096


@dataclass
class LintWarning:
    key: str
    code: str
    message: str


@dataclass
class LintResult:
    warnings: List[LintWarning] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.is_clean:
            return "No lint warnings."
        lines = [f"{len(self.warnings)} warning(s) found:"]
        for w in self.warnings:
            lines.append(f"  [{w.code}] {w.key}: {w.message}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "clean": self.is_clean,
            "warnings": [
                {"key": w.key, "code": w.code, "message": w.message}
                for w in self.warnings
            ],
        }


def lint_snapshot(
    snapshot: Dict[str, str],
    check_sensitive: bool = True,
    check_placeholders: bool = True,
    check_empty_values: bool = True,
    check_value_length: bool = True,
    allowed_sensitive: Optional[List[str]] = None,
) -> LintResult:
    """Run lint checks against a snapshot dict and return a LintResult."""
    result = LintResult()
    allowed = set(allowed_sensitive or [])

    for key, value in snapshot.items():
        if check_sensitive and key not in allowed:
            for pat in SENSITIVE_PATTERNS:
                if pat.search(key):
                    result.warnings.append(
                        LintWarning(
                            key=key,
                            code="SENSITIVE_KEY",
                            message="Key name suggests sensitive data; consider encrypting this snapshot.",
                        )
                    )
                    break

        if check_placeholders and PLACEHOLDER_PATTERN.match(value):
            result.warnings.append(
                LintWarning(
                    key=key,
                    code="PLACEHOLDER_VALUE",
                    message=f"Value looks like a placeholder: {value!r}",
                )
            )

        if check_empty_values and value == "":
            result.warnings.append(
                LintWarning(
                    key=key,
                    code="EMPTY_VALUE",
                    message="Value is an empty string.",
                )
            )

        if check_value_length and len(value) > MAX_VALUE_LENGTH:
            result.warnings.append(
                LintWarning(
                    key=key,
                    code="VALUE_TOO_LONG",
                    message=f"Value exceeds {MAX_VALUE_LENGTH} characters ({len(value)} chars).",
                )
            )

    return result
