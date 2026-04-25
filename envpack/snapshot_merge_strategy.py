"""Advanced merge strategies for combining multiple snapshots.

Provides pluggable strategy objects and a registry so callers can select
merge behaviour by name, extend with custom strategies, and get a full
conflict report rather than just the final merged snapshot.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MergeConflict:
    """Records a key whose value differed across two or more snapshots."""
    key: str
    values: List[str]          # one entry per snapshot that contained the key
    chosen: str                 # the value that was ultimately selected
    strategy_used: str          # name of the strategy that resolved it

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "values": self.values,
            "chosen": self.chosen,
            "strategy_used": self.strategy_used,
        }


@dataclass
class StrategyMergeResult:
    """Result returned by :func:`merge_with_strategy`."""
    merged: Dict[str, str]
    conflicts: List[MergeConflict] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def summary(self) -> str:
        lines = [f"Merged {len(self.merged)} key(s)."]
        if self.conflicts:
            lines.append(f"{len(self.conflicts)} conflict(s) resolved:")
            for c in self.conflicts:
                lines.append(
                    f"  {c.key}: {len(c.values)} differing values "
                    f"-> chose '{c.chosen}' ({c.strategy_used})"
                )
        else:
            lines.append("No conflicts.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Strategy implementations
# ---------------------------------------------------------------------------

class BaseStrategy:
    """Abstract base for merge strategies."""

    name: str = "base"

    def resolve(self, key: str, values: List[str]) -> str:  # pragma: no cover
        raise NotImplementedError


class LastWinsStrategy(BaseStrategy):
    """Always picks the value from the last snapshot that defined the key."""
    name = "last"

    def resolve(self, key: str, values: List[str]) -> str:
        return values[-1]


class FirstWinsStrategy(BaseStrategy):
    """Always picks the value from the first snapshot that defined the key."""
    name = "first"

    def resolve(self, key: str, values: List[str]) -> str:
        return values[0]


class LongestWinsStrategy(BaseStrategy):
    """Picks the longest value string; ties broken by last occurrence."""
    name = "longest"

    def resolve(self, key: str, values: List[str]) -> str:
        return max(values, key=len)


class ShortestWinsStrategy(BaseStrategy):
    """Picks the shortest value string; ties broken by first occurrence."""
    name = "shortest"

    def resolve(self, key: str, values: List[str]) -> str:
        return min(values, key=len)


# ---------------------------------------------------------------------------
# Strategy registry
# ---------------------------------------------------------------------------

_REGISTRY: Dict[str, BaseStrategy] = {}


def _register_defaults() -> None:
    for cls in (LastWinsStrategy, FirstWinsStrategy,
                LongestWinsStrategy, ShortestWinsStrategy):
        inst = cls()
        _REGISTRY[inst.name] = inst


_register_defaults()


def register_strategy(strategy: BaseStrategy) -> None:
    """Add a custom strategy to the registry under its *name* attribute."""
    _REGISTRY[strategy.name] = strategy


def available_strategies() -> List[str]:
    """Return a sorted list of registered strategy names."""
    return sorted(_REGISTRY.keys())


# ---------------------------------------------------------------------------
# Core merge function
# ---------------------------------------------------------------------------

def merge_with_strategy(
    snapshots: List[Dict[str, str]],
    strategy: str = "last",
    override: Optional[Dict[str, str]] = None,
) -> StrategyMergeResult:
    """Merge *snapshots* using the named *strategy*.

    Parameters
    ----------
    snapshots:
        Ordered list of snapshot dicts to merge.
    strategy:
        Name of a registered :class:`BaseStrategy`.  Defaults to ``"last"``.
    override:
        Optional mapping of key -> value that is applied *after* the merge,
        unconditionally overriding any resolved value.

    Returns
    -------
    StrategyMergeResult
        Contains the merged snapshot and a list of resolved conflicts.
    """
    if not snapshots:
        return StrategyMergeResult(merged={}, conflicts=[])

    if strategy not in _REGISTRY:
        raise ValueError(
            f"Unknown merge strategy '{strategy}'. "
            f"Available: {available_strategies()}"
        )

    resolver = _REGISTRY[strategy]

    # Collect all values per key, preserving snapshot order
    key_values: Dict[str, List[str]] = {}
    for snap in snapshots:
        for k, v in snap.items():
            key_values.setdefault(k, []).append(v)

    merged: Dict[str, str] = {}
    conflicts: List[MergeConflict] = []

    for key, values in key_values.items():
        # Deduplicate while preserving order for conflict detection
        unique = list(dict.fromkeys(values))
        if len(unique) == 1:
            merged[key] = unique[0]
        else:
            chosen = resolver.resolve(key, values)
            merged[key] = chosen
            conflicts.append(
                MergeConflict(
                    key=key,
                    values=values,
                    chosen=chosen,
                    strategy_used=resolver.name,
                )
            )

    # Apply manual overrides last
    if override:
        merged.update(override)

    return StrategyMergeResult(merged=merged, conflicts=conflicts)
