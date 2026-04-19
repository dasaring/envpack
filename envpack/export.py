"""Export snapshots to various formats (dotenv, JSON, YAML)."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict

from envpack.snapshot import load


SUPPORTED_FORMATS = ("dotenv", "json", "yaml")


def _requires_yaml():
    try:
        import yaml
        return yaml
    except ImportError:
        raise ImportError("PyYAML is required for YAML export: pip install pyyaml")


def to_dotenv(snapshot: Dict[str, str]) -> str:
    """Render snapshot as .env file content."""
    lines = []
    for key, value in sorted(snapshot.items()):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def to_json(snapshot: Dict[str, str], indent: int = 2) -> str:
    """Render snapshot as JSON."""
    return json.dumps(snapshot, indent=indent, sort_keys=True)


def to_yaml(snapshot: Dict[str, str]) -> str:
    """Render snapshot as YAML."""
    yaml = _requires_yaml()
    return yaml.dump(dict(sorted(snapshot.items())), default_flow_style=False)


def export_snapshot(snapshot_path: str, fmt: str, output_path: str | None = None) -> str:
    """Load a snapshot file and export it in the given format.

    Returns the rendered string and optionally writes it to output_path.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")

    snapshot = load(snapshot_path)

    if fmt == "dotenv":
        content = to_dotenv(snapshot)
    elif fmt == "json":
        content = to_json(snapshot)
    else:
        content = to_yaml(snapshot)

    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")

    return content
