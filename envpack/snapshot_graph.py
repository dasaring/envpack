"""Build and query a dependency graph of snapshots based on history and chains."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Set

from envpack.history import list_history


class GraphNode:
    def __init__(self, snapshot_path: str, label: Optional[str] = None):
        self.snapshot_path = snapshot_path
        self.label = label
        self.children: List[str] = []
        self.parents: List[str] = []

    def to_dict(self) -> dict:
        return {
            "snapshot_path": self.snapshot_path,
            "label": self.label,
            "children": self.children,
            "parents": self.parents,
        }


def build_graph(history_file: Path) -> Dict[str, GraphNode]:
    """Build a directed graph from history entries ordered by timestamp."""
    entries = list_history(history_file)
    if not entries:
        return {}

    graph: Dict[str, GraphNode] = {}
    ordered_paths: List[str] = []

    for entry in entries:
        path = entry["snapshot_path"]
        if path not in graph:
            graph[path] = GraphNode(path, label=entry.get("label"))
        ordered_paths.append(path)

    for i in range(1, len(ordered_paths)):
        parent = ordered_paths[i - 1]
        child = ordered_paths[i]
        if child not in graph[parent].children:
            graph[parent].children.append(child)
        if parent not in graph[child].parents:
            graph[child].parents.append(parent)

    return graph


def roots(graph: Dict[str, GraphNode]) -> List[str]:
    """Return nodes with no parents (entry points)."""
    return [path for path, node in graph.items() if not node.parents]


def leaves(graph: Dict[str, GraphNode]) -> List[str]:
    """Return nodes with no children (latest snapshots)."""
    return [path for path, node in graph.items() if not node.children]


def ancestors(graph: Dict[str, GraphNode], path: str) -> List[str]:
    """Return all ancestor paths of a given node (breadth-first)."""
    visited: Set[str] = set()
    queue = list(graph.get(path, GraphNode(path)).parents)
    result: List[str] = []
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        result.append(current)
        queue.extend(graph.get(current, GraphNode(current)).parents)
    return result


def descendants(graph: Dict[str, GraphNode], path: str) -> List[str]:
    """Return all descendant paths of a given node (breadth-first)."""
    visited: Set[str] = set()
    queue = list(graph.get(path, GraphNode(path)).children)
    result: List[str] = []
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        result.append(current)
        queue.extend(graph.get(current, GraphNode(current)).children)
    return result
