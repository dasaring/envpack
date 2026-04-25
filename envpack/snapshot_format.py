"""snapshot_format.py — convert snapshots between serialisation formats (JSON, dotenv, YAML)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict

from envpack.snapshot import load


class FormatError(Exception):
    """Raised when a format conversion fails."""


_SUPPORTED = {"json", "dotenv", "yaml"}


def _requires_yaml() -> None:
    try:
        import yaml  # noqa: F401
    except ImportError:
        raise FormatError("PyYAML is required for YAML support: pip install pyyaml")


def snapshot_to_json(snapshot: Dict[str, str], *, indent: int = 2) -> str:
    """Serialise *snapshot* as a pretty-printed JSON string."""
    return json.dumps(snapshot, indent=indent, sort_keys=True)


def snapshot_to_dotenv(snapshot: Dict[str, str]) -> str:
    """Serialise *snapshot* as a .env file string."""
    lines = []
    for key in sorted(snapshot):
        value = snapshot[key]
        # Escape double-quotes and newlines inside the value
        escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def snapshot_to_yaml(snapshot: Dict[str, str]) -> str:
    """Serialise *snapshot* as a YAML string."""
    _requires_yaml()
    import yaml
    return yaml.dump(dict(sorted(snapshot.items())), default_flow_style=False, allow_unicode=True)


def convert_file(
    src: str | Path,
    dest: str | Path,
    fmt: str,
) -> Path:
    """Load a JSON snapshot from *src*, convert to *fmt*, and write to *dest*.

    Parameters
    ----------
    src:  path to an existing .json snapshot file
    dest: output path (will be created / overwritten)
    fmt:  one of ``json``, ``dotenv``, ``yaml``

    Returns the resolved *dest* path.
    """
    fmt = fmt.lower()
    if fmt not in _SUPPORTED:
        raise FormatError(f"Unsupported format '{fmt}'. Choose from: {', '.join(sorted(_SUPPORTED))}")

    snapshot = load(str(src))

    if fmt == "json":
        text = snapshot_to_json(snapshot)
    elif fmt == "dotenv":
        text = snapshot_to_dotenv(snapshot)
    else:
        text = snapshot_to_yaml(snapshot)

    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    return dest
