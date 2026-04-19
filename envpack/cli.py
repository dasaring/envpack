"""Command-line interface for envpack."""

import argparse
import sys

from envpack.snapshot import capture, save, load
from envpack.diff import diff_snapshots


def cmd_capture(args: argparse.Namespace) -> None:
    keys = args.keys or None
    snapshot = capture(keys=keys)
    save(snapshot, args.output)
    print(f"Snapshot saved to {args.output} ({len(snapshot)} variables).")


def cmd_diff(args: argparse.Namespace) -> None:
    before = load(args.before)
    after = load(args.after)
    result = diff_snapshots(before, after)
    if result.is_empty():
        print("Snapshots are identical.")
    else:
        added = len(result.added)
        removed = len(result.removed)
        changed = len(result.changed)
        print(f"Diff: +{added} added, -{removed} removed, ~{changed} changed\n")
        print(result.summary())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envpack",
        description="Snapshot, diff, and restore environment variable sets.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # capture subcommand
    capture_parser = subparsers.add_parser("capture", help="Capture current environment.")
    capture_parser.add_argument("output", help="Path to save the snapshot JSON file.")
    capture_parser.add_argument(
        "--keys", nargs="+", metavar="KEY", help="Specific keys to capture."
    )

    # diff subcommand
    diff_parser = subparsers.add_parser("diff", help="Diff two snapshot files.")
    diff_parser.add_argument("before", help="Path to the earlier snapshot.")
    diff_parser.add_argument("after", help="Path to the later snapshot.")

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    dispatch = {
        "capture": cmd_capture,
        "diff": cmd_diff,
    }

    try:
        dispatch[args.command](args)
        return 0
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
