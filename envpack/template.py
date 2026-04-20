"""Template support: create a snapshot with placeholder values for sharing."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

PLACEHOLDER = "<CHANGE_ME>"
_SENSITIVE_RE = re.compile(
    r"(secret|password|passwd|token|key|api|auth|credential|private)",
    re.IGNORECASE,
)


def to_template(
    snapshot: Dict[str, str],
    sensitive_keys: Optional[List[str]] = None,
    mask_auto: bool = True,
) -> Dict[str, str]:
    """Return a copy of *snapshot* with sensitive values replaced by a placeholder."""
    result: Dict[str, str] = {}
    sensitive_set = set(sensitive_keys or [])
    for key, value in snapshot.items():
        if key in sensitive_set or (mask_auto and _SENSITIVE_RE.search(key)):
            result[key] = PLACEHOLDER
        else:
            result[key] = value
    return result


def save_template(template: Dict[str, str], path: str | Path) -> Path:
    """Save a template snapshot to *path* as JSON."""
    dest = Path(path)
    dest.write_text(json.dumps(template, indent=2, sort_keys=True))
    return dest


def load_template(path: str | Path) -> Dict[str, str]:
    """Load a template snapshot from *path*."""
    return json.loads(Path(path).read_text())


def fill_template(
    template: Dict[str, str],
    values: Dict[str, str],
    strict: bool = False,
) -> Dict[str, str]:
    """Fill placeholders in *template* with entries from *values*.

    If *strict* is True, raise ValueError for any unfilled placeholder.
    """
    result = dict(template)
    for key, val in result.items():
        if val == PLACEHOLDER:
            if key in values:
                result[key] = values[key]
            elif strict:
                raise ValueError(f"No value supplied for placeholder key: {key!r}")
    return result


def unfilled_keys(template: Dict[str, str]) -> List[str]:
    """Return list of keys that still hold the placeholder value."""
    return [k for k, v in template.items() if v == PLACEHOLDER]
