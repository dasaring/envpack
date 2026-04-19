"""CLI entry point for envpack."""

import argparse
import sys

from envpack.snapshot import capture, save
from envpack.diff import diff_snapshots
from envpack.restore import generate_export_script, write_restore_script


def cmd_capture(args):
    keys = args.keys.split(",") if args.keys else None
    snapshot = capture(keys=keys)
    save(snapshot, args.output)
    print(f"Snapshot saved to {args.output} ({len(snapshot)} variables)")


def cmd_diff(args):
    result = diff_snapshots(args.snapshot_a, args.snapshot_b)
    if result.is_empty():
        print("No differences found.")
    else:
        print(result.summary())


def cmd_restore(args):
    if args.output:
        write_restore_script(args.snapshot, args.output, shell=args.shell)
        print(f"Restore script written to {args.output}")
    else:
        script = generate_export_script(args.snapshot, shell=args.shell)
        sys.stdout.write(script)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="envpack",
        description="Snapshot, diff, and restore environment variable sets.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # capture
    p_capture = subparsers.add_parser("capture", help="Capture current environment")
    p_capture.add_argument("output", help="Output snapshot file path")
    p_capture.add_argument("--keys", help="Comma-separated list of keys to capture")
    p_capture.set_defaults(func=cmd_capture)

    # diff
    p_diff = subparsers.add_parser("diff", help="Diff two snapshots")
    p_diff.add_argument("snapshot_a", help="First snapshot file")
    p_diff.add_argument("snapshot_b", help="Second snapshot file")
    p_diff.set_defaults(func=cmd_diff)

    # restore
    p_restore = subparsers.add_parser("restore", help="Restore a snapshot as shell exports")
    p_restore.add_argument("snapshot", help="Snapshot file to restore")
    p_restore.add_argument("--output", help="Write script to file instead of stdout")
    p_restore.add_argument(
        "--shell",
        default="bash",
        choices=["bash", "zsh", "sh", "fish"],
        help="Target shell (default: bash)",
    )
    p_restore.set_defaults(func=cmd_restore)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
