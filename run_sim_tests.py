#!/usr/bin/env python3
"""Unified simulator/MCP test runner with optional coverage reporting."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable


@dataclass(frozen=True)
class TestStep:
    """Single runnable test step."""

    name: str
    description: str
    command: List[str]
    coverage_args: List[str]


STEPS: List[TestStep] = [
    TestStep(
        name="python-unit",
        description="Core Python unit tests (tests package)",
        command=[PYTHON, "-m", "tests"],
        coverage_args=["-m", "tests"],
    ),
    TestStep(
        name="asm",
        description="Assembly instruction tests (asm_tests/run_tests.py)",
        command=[PYTHON, str(ROOT / "asm_tests" / "run_tests.py")],
        coverage_args=[str(ROOT / "asm_tests" / "run_tests.py")],
    ),
    TestStep(
        name="c-runtime",
        description="C runtime/syscall tests (tests/c)",
        command=[PYTHON, str(ROOT / "run_c_tests.py")],
        coverage_args=[str(ROOT / "run_c_tests.py")],
    ),
]


def build_command(step: TestStep, coverage_cmd: str | None, parallel: bool) -> List[str]:
    """Return the command used to execute *step*."""

    if coverage_cmd is None:
        return step.command

    args = [coverage_cmd, "run"]
    if parallel:
        args.append("--parallel-mode")
    args.extend(step.coverage_args)
    return args


def run_step(step: TestStep, coverage_cmd: str | None, parallel: bool) -> None:
    """Run a single step and raise on failure."""

    cmd = build_command(step, coverage_cmd, parallel)
    pretty = " ".join(cmd)
    print(f"\n=== {step.name}: {step.description} ===")
    print(f"$ {pretty}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"Step '{step.name}' failed with exit code {result.returncode}")


def parse_args() -> argparse.Namespace:
    step_names = [step.name for step in STEPS]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage instrumentation (default: enabled if coverage is installed)",
    )
    parser.add_argument(
        "--fail-under",
        type=int,
        default=os.environ.get("PYRV32_COVERAGE_FAIL_UNDER"),
        help="Minimum coverage percentage required (overrides PYRV32_COVERAGE_FAIL_UNDER env)",
    )
    parser.add_argument(
        "--skip",
        action="append",
        choices=step_names,
        help="Skip specific steps (may be used multiple times)",
    )
    parser.add_argument(
        "--only",
        action="append",
        choices=step_names,
        help="Run only the specified steps (preserves declaration order)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available steps and exit",
    )
    return parser.parse_args()


def list_steps() -> None:
    for step in STEPS:
        print(f"{step.name:12s} - {step.description}")


def select_steps(args: argparse.Namespace) -> List[TestStep]:
    chosen = []
    for step in STEPS:
        if args.only and step.name not in args.only:
            continue
        if args.skip and step.name in args.skip:
            continue
        chosen.append(step)
    if not chosen:
        raise SystemExit("No test steps selected")
    return chosen


def ensure_coverage(args: argparse.Namespace) -> str | None:
    if args.no_coverage:
        return None
    coverage_cmd = shutil.which("coverage")
    if coverage_cmd is None:
        raise SystemExit(
            "coverage not found in PATH. Install it (pip install coverage) or rerun with --no-coverage."
        )
    # Reset previous data so each run starts clean.
    subprocess.run([coverage_cmd, "erase"], cwd=ROOT, check=True)
    return coverage_cmd


def finalize_coverage(coverage_cmd: str | None, fail_under: int | None) -> None:
    if coverage_cmd is None:
        return
    subprocess.run([coverage_cmd, "combine"], cwd=ROOT, check=True)
    report_cmd = [coverage_cmd, "report", "-m"]
    if fail_under is not None:
        report_cmd += ["--fail-under", str(fail_under)]
    subprocess.run(report_cmd, cwd=ROOT, check=True)


def main() -> None:
    args = parse_args()

    if args.list:
        list_steps()
        return

    steps = select_steps(args)
    coverage_cmd = ensure_coverage(args)

    try:
        for step in steps:
            run_step(step, coverage_cmd, parallel=True)
    except RuntimeError as exc:
        print(f"\n❌ {exc}")
        raise SystemExit(1)

    finalize_coverage(coverage_cmd, int(args.fail_under) if args.fail_under is not None else None)
    print("\n✅ All selected tests passed")


if __name__ == "__main__":
    main()
