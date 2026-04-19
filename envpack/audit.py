"""Audit log for snapshot operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DEFAULT_AUDIT_LOG = Path.home() / ".envpack" / "audit.log"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(
    action: str,
    path: Optional[str] = None,
    keys_count: Optional[int] = None,
    extra: Optional[dict] = None,
    log_file: Path = DEFAULT_AUDIT_LOG,
) -> dict:
    """Append a structured audit event to the log file and return the event."""
    event = {
        "timestamp": _now_iso(),
        "action": action,
    }
    if path is not None:
        event["path"] = str(path)
    if keys_count is not None:
        event["keys_count"] = keys_count
    if extra:
        event.update(extra)

    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")

    return event


def read_events(log_file: Path = DEFAULT_AUDIT_LOG) -> list[dict]:
    """Return all audit events from the log file."""
    if not log_file.exists():
        return []
    events = []
    with log_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def clear_log(log_file: Path = DEFAULT_AUDIT_LOG) -> None:
    """Delete the audit log file if it exists."""
    if log_file.exists():
        log_file.unlink()
