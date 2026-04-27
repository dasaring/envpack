"""Score snapshots based on quality heuristics (size, redaction, validation, lint)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envpack.snapshot import load
from envpack.lint import lint_snapshot
from envpack.validate import validate_snapshot
from envpack.redact import redacted_keys


@dataclass
class ScoreResult:
    path: str
    total: int
    max_score: int
    breakdown: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)

    @property
    def percent(self) -> float:
        if self.max_score == 0:
            return 0.0
        return round(self.total / self.max_score * 100, 1)

    def summary(self) -> str:
        lines = [f"Score: {self.total}/{self.max_score} ({self.percent}%)"]
        for k, v in self.breakdown.items():
            lines.append(f"  {k}: {v}")
        for note in self.notes:
            lines.append(f"  ! {note}")
        return "\n".join(lines)


def score_snapshot(
    path: str | Path,
    required_keys: Optional[list] = None,
    schema: Optional[dict] = None,
) -> ScoreResult:
    """Compute a quality score for a snapshot file."""
    p = Path(path)
    snapshot = load(str(p))
    breakdown: dict = {}
    notes: list = []
    total = 0
    max_score = 0

    # Criterion 1: non-empty (10 pts)
    max_score += 10
    if snapshot:
        breakdown["non_empty"] = 10
        total += 10
    else:
        breakdown["non_empty"] = 0
        notes.append("Snapshot is empty")

    # Criterion 2: no lint warnings (30 pts)
    max_score += 30
    lint = lint_snapshot(snapshot)
    if lint.is_clean():
        breakdown["lint_clean"] = 30
        total += 30
    else:
        deduction = min(30, len(lint.warnings) * 5)
        pts = max(0, 30 - deduction)
        breakdown["lint_clean"] = pts
        total += pts
        notes.append(f"{len(lint.warnings)} lint warning(s) found")

    # Criterion 3: no unredacted sensitive keys (30 pts)
    max_score += 30
    exposed = redacted_keys(snapshot)
    if not exposed:
        breakdown["no_exposed_secrets"] = 30
        total += 30
    else:
        pts = max(0, 30 - len(exposed) * 6)
        breakdown["no_exposed_secrets"] = pts
        total += pts
        notes.append(f"{len(exposed)} sensitive key(s) have real values")

    # Criterion 4: required keys present (30 pts)
    max_score += 30
    if required_keys:
        missing = [k for k in required_keys if k not in snapshot]
        if not missing:
            breakdown["required_keys"] = 30
            total += 30
        else:
            pts = max(0, 30 - len(missing) * 10)
            breakdown["required_keys"] = pts
            total += pts
            notes.append(f"Missing required keys: {', '.join(missing)}")
    else:
        breakdown["required_keys"] = 30
        total += 30

    return ScoreResult(
        path=str(p),
        total=total,
        max_score=max_score,
        breakdown=breakdown,
        notes=notes,
    )
