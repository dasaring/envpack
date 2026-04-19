"""Snapshot module: capture and serialize environment variable sets."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_SNAPSHOT_DIR = Path(".envpack")


def capture(name: str, keys: list[str] | None = None) -> dict:
    """Capture current environment variables into a snapshot dict.

    Args:
        name: Human-readable label for this snapshot.
        keys: Optional list of specific keys to capture. Captures all if None.

    Returns:
        A snapshot dictionary with metadata and variables.
    """
    env = os.environ.copy()
    if keys is not None:
        env = {k: env[k] for k in keys if k in env}

    return {
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "variables": env,
    }


def save(snapshot: dict, directory: Path = DEFAULT_SNAPSHOT_DIR) -> Path:
    """Persist a snapshot to disk as a JSON file.

    Args:
        snapshot: Snapshot dict produced by `capture`.
        directory: Directory to store snapshot files.

    Returns:
        Path to the written snapshot file.
    """
    directory.mkdir(parents=True, exist_ok=True)
    safe_name = snapshot["name"].replace(" ", "_")
    filename = directory / f"{safe_name}.json"
    filename.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return filename


def load(path: Path) -> dict:
    """Load a snapshot from a JSON file.

    Args:
        path: Path to the snapshot JSON file.

    Returns:
        Snapshot dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not valid JSON or missing required keys.
    """
    if not path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in snapshot file: {path}") from exc
    for required in ("name", "created_at", "variables"):
        if required not in data:
            raise ValueError(f"Snapshot missing required key: '{required}'")
    return data
