r"""Run phase-scoped deterministic tests and report failures by phase.

Usage on Windows:
    .\.venv\Scripts\python.exe scripts\run_phase_validation.py --phase all

The runner performs no model inference and no repository mutation.  It maps
failures to the phase that owns the relevant deterministic contract.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHASE_TESTS: dict[str, tuple[str, ...]] = {
    "phase00": ("agent_solution/tests/unit/test_paths.py",),
    "phase02": (
        "agent_solution/tests/test_intake.py",
        "agent_solution/tests/test_git_context.py",
    ),
    "phase03": (
        "agent_solution/tests/test_grounded_analysis.py",
        "agent_solution/tests/test_local_model_runner.py",
    ),
    "phase04": ("agent_solution/tests/test_patch_validation.py",),
    "phase05": ("agent_solution/tests/test_readiness.py",),
}


@dataclass
class StepResult:
    name: str
    passed: bool
    exit_code: int
    duration_ms: int
    output: str


def _run(name: str, command: list[str]) -> StepResult:
    start = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return StepResult(
        name=name,
        passed=completed.returncode == 0,
        exit_code=completed.returncode,
        duration_ms=int((time.monotonic() - start) * 1000),
        output=completed.stdout[-12_000:],
    )


def _hygiene_steps() -> list[StepResult]:
    results = [_run("ruff", [sys.executable, "-m", "ruff", "check", "agent_solution", "scripts"])]
    if shutil.which("git"):
        results.append(_run("git_diff_check", ["git", "diff", "--check"]))
    else:
        results.append(
            StepResult(
                name="git_diff_check",
                passed=False,
                exit_code=-1,
                duration_ms=0,
                output="git executable not found on PATH",
            )
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase",
        choices=["all", *PHASE_TESTS],
        default="all",
        help="Phase group to run; default runs all groups.",
    )
    parser.add_argument(
        "--no-hygiene",
        action="store_true",
        help="Skip Ruff and git diff --check.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON summary as the final line.",
    )
    args = parser.parse_args()

    selected = list(PHASE_TESTS) if args.phase == "all" else [args.phase]
    results: list[StepResult] = []
    for phase in selected:
        result = _run(phase, [sys.executable, "-m", "pytest", "-q", *PHASE_TESTS[phase]])
        results.append(result)
        marker = "PASS" if result.passed else "FAIL"
        print(f"[{marker}] {phase} ({result.duration_ms} ms)")
        if not result.passed:
            print(result.output)

    if not args.no_hygiene:
        for result in _hygiene_steps():
            results.append(result)
            marker = "PASS" if result.passed else "FAIL"
            print(f"[{marker}] {result.name} ({result.duration_ms} ms)")
            if not result.passed:
                print(result.output)

    summary = {
        "all_passed": all(result.passed for result in results),
        "results": [asdict(result) for result in results],
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        print("\nValidation summary:")
        for result in results:
            marker = "PASS" if result.passed else "FAIL"
            print(f"- {marker}: {result.name}")
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
