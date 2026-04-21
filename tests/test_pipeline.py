"""Tests for envpack.pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envpack.pipeline import PipelineError, PipelineResult, StepResult, run_pipeline
from envpack.snapshot import save


@pytest.fixture()
def snap_file(tmp_path: Path) -> Path:
    path = tmp_path / "snap.json"
    save({"HOME": "/home/user", "PATH": "/usr/bin", "APP_NAME": "envpack"}, path)
    return path


@pytest.fixture()
def snap_with_secret(tmp_path: Path) -> Path:
    path = tmp_path / "secret_snap.json"
    save({"APP_PASSWORD": "hunter2", "APP_NAME": "envpack"}, path)
    return path


def test_pipeline_result_success_when_all_steps_ok():
    pr = PipelineResult(
        steps=[
            StepResult(name="lint", success=True),
            StepResult(name="validate", success=True),
        ]
    )
    assert pr.success is True


def test_pipeline_result_failure_when_any_step_fails():
    pr = PipelineResult(
        steps=[
            StepResult(name="lint", success=True),
            StepResult(name="validate", success=False, message="missing KEY"),
        ]
    )
    assert pr.success is False


def test_pipeline_result_summary_contains_step_names():
    pr = PipelineResult(
        steps=[
            StepResult(name="lint", success=True, message="no warnings"),
            StepResult(name="validate", success=False, message="missing KEY"),
        ]
    )
    s = pr.summary()
    assert "lint" in s
    assert "validate" in s
    assert "OK" in s
    assert "FAIL" in s


def test_pipeline_result_to_dict(snap_file: Path):
    result = run_pipeline(snap_file, steps=["lint"])
    d = result.to_dict()
    assert "success" in d
    assert "steps" in d
    assert isinstance(d["steps"], list)


def test_run_pipeline_load_step_always_present(snap_file: Path):
    result = run_pipeline(snap_file, steps=["lint"])
    names = [s.name for s in result.steps]
    assert "load" in names


def test_run_pipeline_lint_step_clean_snapshot(snap_file: Path):
    result = run_pipeline(snap_file, steps=["lint"])
    lint_step = next(s for s in result.steps if s.name == "lint")
    assert lint_step.success is True


def test_run_pipeline_lint_step_sensitive_key(snap_with_secret: Path):
    result = run_pipeline(snap_with_secret, steps=["lint"])
    lint_step = next(s for s in result.steps if s.name == "lint")
    assert lint_step.success is False


def test_run_pipeline_lint_allowed_keys_suppresses_warning(snap_with_secret: Path):
    result = run_pipeline(
        snap_with_secret, steps=["lint"], lint_allowed_keys=["APP_PASSWORD"]
    )
    lint_step = next(s for s in result.steps if s.name == "lint")
    assert lint_step.success is True


def test_run_pipeline_validate_missing_required(snap_file: Path):
    result = run_pipeline(snap_file, steps=["validate"], validate_required=["MISSING_KEY"])
    val_step = next(s for s in result.steps if s.name == "validate")
    assert val_step.success is False


def test_run_pipeline_validate_required_present(snap_file: Path):
    result = run_pipeline(snap_file, steps=["validate"], validate_required=["APP_NAME"])
    val_step = next(s for s in result.steps if s.name == "validate")
    assert val_step.success is True


def test_run_pipeline_export_step(snap_file: Path, tmp_path: Path):
    dest = tmp_path / "out.json"
    result = run_pipeline(
        snap_file, steps=["export"], export_format="json", export_path=dest
    )
    export_step = next(s for s in result.steps if s.name == "export")
    assert export_step.success is True
    assert dest.exists()


def test_run_pipeline_export_without_path(snap_file: Path):
    result = run_pipeline(snap_file, steps=["export"])
    export_step = next(s for s in result.steps if s.name == "export")
    assert export_step.success is False
    assert "export_path" in export_step.message


def test_run_pipeline_unknown_step(snap_file: Path):
    result = run_pipeline(snap_file, steps=["frobnicate"])
    step = next(s for s in result.steps if s.name == "frobnicate")
    assert step.success is False
    assert "unknown" in step.message


def test_run_pipeline_halt_on_error_raises(snap_with_secret: Path):
    with pytest.raises(PipelineError):
        run_pipeline(snap_with_secret, steps=["lint"], halt_on_error=True)


def test_run_pipeline_missing_file(tmp_path: Path):
    result = run_pipeline(tmp_path / "nope.json", steps=["lint"])
    load_step = next(s for s in result.steps if s.name == "load")
    assert load_step.success is False
    assert result.success is False
