"""notify.py — simple notification hooks for envpack events.

Supports calling user-defined webhook URLs or running shell commands
when key envpack events occur (e.g. snapshot captured, restore applied).

Notification config is stored in a JSON file (default: ~/.envpack_notify.json).
"""

import json
import os
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

DEFAULT_NOTIFY_FILE = Path.home() / ".envpack_notify.json"

# Supported event names
EVENTS = {
    "capture",
    "restore",
    "diff",
    "prune",
    "rollback",
}


def _load_config(notify_file: Path) -> dict:
    """Load notification config from *notify_file*, returning empty dict if missing."""
    if not notify_file.exists():
        return {}
    with notify_file.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_config(config: dict, notify_file: Path) -> None:
    """Persist *config* to *notify_file*."""
    notify_file.parent.mkdir(parents=True, exist_ok=True)
    with notify_file.open("w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)


def add_webhook(
    event: str,
    url: str,
    notify_file: Path = DEFAULT_NOTIFY_FILE,
) -> bool:
    """Register *url* as a webhook for *event*.

    Returns True if the entry was newly added, False if it already existed.
    Raises ValueError for unknown event names.
    """
    if event not in EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid events: {sorted(EVENTS)}")
    config = _load_config(notify_file)
    webhooks: list = config.setdefault("webhooks", {}).setdefault(event, [])
    if url in webhooks:
        return False
    webhooks.append(url)
    _save_config(config, notify_file)
    return True


def add_command(
    event: str,
    command: str,
    notify_file: Path = DEFAULT_NOTIFY_FILE,
) -> bool:
    """Register a shell *command* to run when *event* fires.

    Returns True if newly added, False if already present.
    """
    if event not in EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid events: {sorted(EVENTS)}")
    config = _load_config(notify_file)
    commands: list = config.setdefault("commands", {}).setdefault(event, [])
    if command in commands:
        return False
    commands.append(command)
    _save_config(config, notify_file)
    return True


def remove_webhook(
    event: str,
    url: str,
    notify_file: Path = DEFAULT_NOTIFY_FILE,
) -> bool:
    """Remove *url* webhook for *event*. Returns True if removed, False if not found."""
    config = _load_config(notify_file)
    webhooks: list = config.get("webhooks", {}).get(event, [])
    if url not in webhooks:
        return False
    webhooks.remove(url)
    _save_config(config, notify_file)
    return True


def notify(
    event: str,
    payload: dict[str, Any],
    notify_file: Path = DEFAULT_NOTIFY_FILE,
) -> dict[str, list[str]]:
    """Fire all registered webhooks and commands for *event*.

    *payload* is serialised as JSON and sent as the POST body for webhooks,
    and injected into the environment as ENVPACK_EVENT and ENVPACK_PAYLOAD
    for shell commands.

    Returns a dict with keys 'errors' (list of error strings) and
    'fired' (list of descriptions of successfully fired notifications).
    """
    config = _load_config(notify_file)
    errors: list[str] = []
    fired: list[str] = []

    body = json.dumps({"event": event, **payload}).encode("utf-8")

    # --- webhooks ---
    for url in config.get("webhooks", {}).get(event, []):
        try:
            req = urllib.request.Request(
                url,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5):
                pass
            fired.append(f"webhook:{url}")
        except urllib.error.URLError as exc:
            errors.append(f"webhook:{url} failed: {exc}")

    # --- shell commands ---
    env = os.environ.copy()
    env["ENVPACK_EVENT"] = event
    env["ENVPACK_PAYLOAD"] = body.decode("utf-8")
    for cmd in config.get("commands", {}).get(event, []):
        try:
            subprocess.run(cmd, shell=True, env=env, check=True)  # noqa: S602
            fired.append(f"command:{cmd}")
        except subprocess.CalledProcessError as exc:
            errors.append(f"command:{cmd!r} exited {exc.returncode}")

    return {"fired": fired, "errors": errors}


def list_notifications(
    notify_file: Path = DEFAULT_NOTIFY_FILE,
) -> dict[str, dict[str, list[str]]]:
    """Return the full notification config grouped by type and event."""
    config = _load_config(notify_file)
    return {
        "webhooks": config.get("webhooks", {}),
        "commands": config.get("commands", {}),
    }
