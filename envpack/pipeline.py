"""Pipeline: chain operations (capture → lint → validate → export) in sequence."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class PipelineError(Exception):
    """Raised when a pipeline step fails and halt_on_error is True."""


@dataclass
class StepResult:
    name: str
    success: bool
    message: str = ""
    data: Any = None


@dataclass
class PipelineResult:
    steps: list[StepResult] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return all(s.success for s in self.steps)

    def summary(self) -> str:
        lines = []
        for s in self.steps:
            status = "OK" if s.success else "FAIL"
            line = f"[{status}] {s.name}"
            if s.message:
                line += f": {s.message}"
            lines.append(line)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "steps": [
                {"name": s.name, "success": s.success, "message": s.message}
                for s in self.steps
            ],
        }


def run_pipeline(
    snapshot_path: str | Path,
    steps: list[str],
    *,
    halt_on_error: bool = False,
    lint_allowed_keys: list[str] | None = None,
    validate_required: list[str] | None = None,
    export_format: str = "json",
    export_path: str | Path | None = None,
) -> PipelineResult:
    """Execute a sequence of named steps against a snapshot file.

    Supported step names: 'lint', 'validate', 'export'.
    """
    from envpack.snapshot import load
    from envpack.lint import lint_snapshot
    from envpack.validate import validate_snapshot
    from envpack.export import export_snapshot

    result = PipelineResult()
    snapshot_path = Path(snapshot_path)

    try:
        snapshot = load(snapshot_path)
    except Exception as exc:  # noqa: BLE001
        step = StepResult(name="load", success=False, message=str(exc))
        result.steps.append(step)
        if halt_on_error:
            raise PipelineError(f"load failed: {exc}") from exc
        return result

    result.steps.append(StepResult(name="load", success=True, message=str(snapshot_path)))

    for step_name in steps:
        if step_name == "lint":
            lr = lint_snapshot(snapshot, allowed_keys=lint_allowed_keys or [])
            ok = lr.is_clean()
            msg = lr.summary() if not ok else "no warnings"
            step = StepResult(name="lint", success=ok, message=msg, data=lr.to_dict())

        elif step_name == "validate":
            vr = validate_snapshot(snapshot, required_keys=validate_required or [])
            ok = vr.is_valid
            msg = vr.summary() if not ok else "all keys valid"
            step = StepResult(name="validate", success=ok, message=msg)

        elif step_name == "export":
            if export_path is None:
                step = StepResult(name="export", success=False, message="export_path not specified")
            else:
                try:
                    export_snapshot(snapshot, fmt=export_format, dest=Path(export_path))
                    step = StepResult(name="export", success=True, message=str(export_path))
                except Exception as exc:  # noqa: BLE001
                    step = StepResult(name="export", success=False, message=str(exc))
        else:
            step = StepResult(name=step_name, success=False, message=f"unknown step '{step_name}'")

        result.steps.append(step)
        if halt_on_error and not step.success:
            raise PipelineError(f"step '{step_name}' failed: {step.message}")

    return result
