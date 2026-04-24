"""CLI commands for the snapshot index feature."""
from __future__ import annotations

import sys

from envpack.snapshot_index import build_index, find_by_key, largest, summary


def cmd_index_build(args) -> None:
    """Print a summary index of all snapshots in a directory."""
    try:
        index = build_index(args.directory)
    except NotADirectoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not index:
        print("No snapshots found.")
        return

    for entry in index:
        captured = entry.captured_at or "unknown"
        print(f"{entry.path}  keys={entry.key_count}  captured_at={captured}  bytes={entry.size_bytes}")

    print()
    print(summary(index))


def cmd_index_find(args) -> None:
    """Find snapshots that contain a given key."""
    try:
        index = build_index(args.directory)
    except NotADirectoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    matches = find_by_key(index, args.key)
    if not matches:
        print(f"No snapshots contain key {args.key!r}.")
        return

    for entry in matches:
        print(entry.path)


def cmd_index_largest(args) -> None:
    """List the N largest snapshots by key count."""
    try:
        index = build_index(args.directory)
    except NotADirectoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    top = largest(index, n=args.n)
    for entry in top:
        print(f"{entry.key_count:>6} keys  {entry.path}")


def register_index_commands(subparsers) -> None:
    p_build = subparsers.add_parser("index-build", help="Index all snapshots in a directory")
    p_build.add_argument("directory", help="Directory to scan")
    p_build.set_defaults(func=cmd_index_build)

    p_find = subparsers.add_parser("index-find", help="Find snapshots containing a key")
    p_find.add_argument("directory", help="Directory to scan")
    p_find.add_argument("key", help="Environment variable key to search for")
    p_find.set_defaults(func=cmd_index_find)

    p_largest = subparsers.add_parser("index-largest", help="List largest snapshots by key count")
    p_largest.add_argument("directory", help="Directory to scan")
    p_largest.add_argument("--n", type=int, default=5, help="Number of results (default: 5)")
    p_largest.set_defaults(func=cmd_index_largest)
