"""CLI subcommands for tagging snapshots."""

import argparse
from envpack.tags import (
    add_tag, remove_tag, get_snapshots_by_tag,
    get_tags_for_snapshot, list_all_tags,
)


def cmd_tag_add(args: argparse.Namespace) -> None:
    """Tag a snapshot file with a label."""
    add_tag(args.snapshot, args.tag)
    print(f"Tagged '{args.snapshot}' with '{args.tag}'.")


def cmd_tag_remove(args: argparse.Namespace) -> None:
    """Remove a tag from a snapshot file."""
    removed = remove_tag(args.snapshot, args.tag)
    if removed:
        print(f"Removed tag '{args.tag}' from '{args.snapshot}'.")
    else:
        print(f"Tag '{args.tag}' not found on '{args.snapshot}'.")


def cmd_tag_list(args: argparse.Namespace) -> None:
    """List tags for a snapshot or all tags."""
    if args.snapshot:
        tags = get_tags_for_snapshot(args.snapshot)
        if tags:
            print(f"Tags for '{args.snapshot}':")
            for t in tags:
                print(f"  {t}")
        else:
            print(f"No tags found for '{args.snapshot}'.")
    else:
        all_tags = list_all_tags()
        if not all_tags:
            print("No tags defined.")
            return
        for tag, paths in all_tags.items():
            print(f"{tag}:")
            for p in paths:
                print(f"  {p}")


def cmd_tag_find(args: argparse.Namespace) -> None:
    """Find all snapshots with a given tag."""
    snapshots = get_snapshots_by_tag(args.tag)
    if snapshots:
        print(f"Snapshots tagged '{args.tag}':")
        for s in snapshots:
            print(f"  {s}")
    else:
        print(f"No snapshots found with tag '{args.tag}'.")


def register_tag_commands(subparsers) -> None:
    """Register tag-related subcommands on the given subparsers object."""
    tag_parser = subparsers.add_parser("tag", help="Manage snapshot tags")
    tag_sub = tag_parser.add_subparsers(dest="tag_cmd", required=True)

    p_add = tag_sub.add_parser("add", help="Add a tag to a snapshot")
    p_add.add_argument("snapshot", help="Path to snapshot file")
    p_add.add_argument("tag", help="Tag label")
    p_add.set_defaults(func=cmd_tag_add)

    p_remove = tag_sub.add_parser("remove", help="Remove a tag from a snapshot")
    p_remove.add_argument("snapshot", help="Path to snapshot file")
    p_remove.add_argument("tag", help="Tag label")
    p_remove.set_defaults(func=cmd_tag_remove)

    p_list = tag_sub.add_parser("list", help="List tags")
    p_list.add_argument("snapshot", nargs="?", default=None, help="Snapshot path (optional)")
    p_list.set_defaults(func=cmd_tag_list)

    p_find = tag_sub.add_parser("find", help="Find snapshots by tag")
    p_find.add_argument("tag", help="Tag label to search")
    p_find.set_defaults(func=cmd_tag_find)
