"""CLI commands for the replay feature."""

from __future__ import annotations

import sys

from envpack.replay import replay, ReplayError

_DEFAULT_HISTORY = ".envpack_history.json"


def cmd_replay(args) -> None:
    """Handle the 'replay' sub-command."""
    history_file = getattr(args, "history_file", _DEFAULT_HISTORY)
    index = getattr(args, "index", None)
    label = getattr(args, "label", None)
    dest = args.dest
    dry_run = getattr(args, "dry_run", False)

    if index is None and label is None:
        print("Error: provide --index or --label.", file=sys.stderr)
        sys.exit(1)

    try:
        source = replay(
            history_file,
            dest,
            index=index,
            label=label,
            dry_run=dry_run,
        )
    except ReplayError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if dry_run:
        print(f"[dry-run] would replay {source} → {dest}")
    else:
        print(f"Replayed {source} → {dest}")


def register_replay_commands(subparsers) -> None:
    """Register the 'replay' sub-command with *subparsers*."""
    p = subparsers.add_parser("replay", help="Re-apply a snapshot from history.")
    p.add_argument("dest", help="Destination path for the replayed snapshot.")
    p.add_argument("--index", type=int, default=None, help="History entry index (0-based).")
    p.add_argument("--label", default=None, help="History entry label.")
    p.add_argument(
        "--history-file",
        dest="history_file",
        default=_DEFAULT_HISTORY,
        help="Path to the history file.",
    )
    p.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Show what would be done without writing files.",
    )
    p.set_defaults(func=cmd_replay)
