"""CLI commands for filtering snapshots by tag combinations."""

from __future__ import annotations

import argparse
from pathlib import Path

from envpack.snapshot_tag_filter import filter_snapshots, TagFilterError


def cmd_tag_filter(args: argparse.Namespace) -> None:
    """Print snapshot paths matching the given tag filter criteria."""
    tags_file = Path(args.tags_file) if getattr(args, "tags_file", None) else None

    any_tags = args.any or []
    all_tags = args.all or []
    exclude_tags = args.exclude or []

    if not any_tags and not all_tags and not exclude_tags:
        print("error: provide at least one of --any, --all, or --exclude", flush=True)
        raise SystemExit(1)

    try:
        results = filter_snapshots(
            any_tags=any_tags or None,
            all_tags=all_tags or None,
            exclude_tags=exclude_tags or None,
            tags_file=tags_file,
        )
    except TagFilterError as exc:
        print(f"error: {exc}", flush=True)
        raise SystemExit(1)

    if not results:
        print("no snapshots matched")
    else:
        for path in results:
            print(path)


def register_tag_filter_commands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "tag-filter",
        help="filter snapshots by tag combinations",
    )
    p.add_argument(
        "--any",
        nargs="+",
        metavar="TAG",
        help="include snapshots with ANY of these tags (union)",
    )
    p.add_argument(
        "--all",
        nargs="+",
        metavar="TAG",
        help="include snapshots with ALL of these tags (intersection)",
    )
    p.add_argument(
        "--exclude",
        nargs="+",
        metavar="TAG",
        help="exclude snapshots with any of these tags",
    )
    p.add_argument(
        "--tags-file",
        default=None,
        metavar="PATH",
        help="path to tags JSON file (default: envpack default)",
    )
    p.set_defaults(func=cmd_tag_filter)
