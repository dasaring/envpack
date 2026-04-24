"""CLI commands for snapshot graph inspection."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envpack.snapshot_graph import build_graph, roots, leaves, ancestors, descendants


def cmd_graph_roots(args: argparse.Namespace) -> None:
    history_file = Path(args.history_file)
    graph = build_graph(history_file)
    result = roots(graph)
    if not result:
        print("No root snapshots found.")
    else:
        for path in result:
            label = graph[path].label
            suffix = f"  [{label}]" if label else ""
            print(f"{path}{suffix}")


def cmd_graph_leaves(args: argparse.Namespace) -> None:
    history_file = Path(args.history_file)
    graph = build_graph(history_file)
    result = leaves(graph)
    if not result:
        print("No leaf snapshots found.")
    else:
        for path in result:
            label = graph[path].label
            suffix = f"  [{label}]" if label else ""
            print(f"{path}{suffix}")


def cmd_graph_ancestors(args: argparse.Namespace) -> None:
    history_file = Path(args.history_file)
    graph = build_graph(history_file)
    result = ancestors(graph, args.snapshot)
    if not result:
        print("No ancestors found.")
    else:
        for path in result:
            print(path)


def cmd_graph_descendants(args: argparse.Namespace) -> None:
    history_file = Path(args.history_file)
    graph = build_graph(history_file)
    result = descendants(graph, args.snapshot)
    if not result:
        print("No descendants found.")
    else:
        for path in result:
            print(path)


def register_graph_commands(subparsers: argparse._SubParsersAction) -> None:
    hf = {"dest": "history_file", "default": ".envpack_history.json",
          "help": "Path to history file"}

    p_roots = subparsers.add_parser("graph-roots", help="Show root snapshots in history graph")
    p_roots.add_argument("--history-file", **hf)
    p_roots.set_defaults(func=cmd_graph_roots)

    p_leaves = subparsers.add_parser("graph-leaves", help="Show leaf snapshots in history graph")
    p_leaves.add_argument("--history-file", **hf)
    p_leaves.set_defaults(func=cmd_graph_leaves)

    p_anc = subparsers.add_parser("graph-ancestors", help="Show ancestors of a snapshot")
    p_anc.add_argument("snapshot", help="Snapshot path to inspect")
    p_anc.add_argument("--history-file", **hf)
    p_anc.set_defaults(func=cmd_graph_ancestors)

    p_desc = subparsers.add_parser("graph-descendants", help="Show descendants of a snapshot")
    p_desc.add_argument("snapshot", help="Snapshot path to inspect")
    p_desc.add_argument("--history-file", **hf)
    p_desc.set_defaults(func=cmd_graph_descendants)
