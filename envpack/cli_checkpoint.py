"""CLI commands for checkpoint management."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envpack.checkpoint import (
    create_checkpoint,
    delete_checkpoint,
    get_checkpoint,
    list_checkpoints,
)


def cmd_checkpoint_create(args: argparse.Namespace) -> None:
    store = Path(args.store)
    entry = create_checkpoint(
        args.name, args.snapshot, description=args.description or "", store=store
    )
    print(f"Checkpoint '{args.name}' -> {entry['snapshot']}")


def cmd_checkpoint_delete(args: argparse.Namespace) -> None:
    store = Path(args.store)
    removed = delete_checkpoint(args.name, store=store)
    if removed:
        print(f"Removed checkpoint '{args.name}'.")
    else:
        print(f"Checkpoint '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)


def cmd_checkpoint_show(args: argparse.Namespace) -> None:
    store = Path(args.store)
    entry = get_checkpoint(args.name, store=store)
    if entry is None:
        print(f"Checkpoint '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    print(f"snapshot : {entry['snapshot']}")
    if entry.get("description"):
        print(f"description: {entry['description']}")


def cmd_checkpoint_list(args: argparse.Namespace) -> None:
    store = Path(args.store)
    checkpoints = list_checkpoints(store=store)
    if not checkpoints:
        print("No checkpoints defined.")
        return
    for name, entry in checkpoints.items():
        desc = f"  # {entry['description']}" if entry.get("description") else ""
        print(f"{name}: {entry['snapshot']}{desc}")


def register_checkpoint_commands(subparsers: argparse._SubParsersAction, default_store: str) -> None:
    common = {"store": default_store}

    p_create = subparsers.add_parser("checkpoint-create", help="Create a checkpoint")
    p_create.add_argument("name")
    p_create.add_argument("snapshot")
    p_create.add_argument("--description", default="")
    p_create.add_argument("--store", default=common["store"])
    p_create.set_defaults(func=cmd_checkpoint_create)

    p_delete = subparsers.add_parser("checkpoint-delete", help="Delete a checkpoint")
    p_delete.add_argument("name")
    p_delete.add_argument("--store", default=common["store"])
    p_delete.set_defaults(func=cmd_checkpoint_delete)

    p_show = subparsers.add_parser("checkpoint-show", help="Show a checkpoint")
    p_show.add_argument("name")
    p_show.add_argument("--store", default=common["store"])
    p_show.set_defaults(func=cmd_checkpoint_show)

    p_list = subparsers.add_parser("checkpoint-list", help="List all checkpoints")
    p_list.add_argument("--store", default=common["store"])
    p_list.set_defaults(func=cmd_checkpoint_list)
