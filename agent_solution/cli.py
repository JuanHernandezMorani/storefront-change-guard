"""CLI interface for Storefront Change Guard.

Provides the analyze subcommand for Phase 03 evidence-grounded analysis.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent_solution import __version__
from agent_solution.core.paths import project_root


def _add_analyze_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Add the analyze subcommand."""
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Run evidence-grounded semantic analysis.",
    )
    analyze_parser.add_argument(
        "--request",
        required=True,
        help="The analysis request text.",
    )
    analyze_parser.add_argument(
        "--repository",
        type=Path,
        default=None,
        help="Repository root path. Defaults to current directory.",
    )
    analyze_parser.add_argument(
        "--language",
        choices=["auto", "en", "es"],
        default="auto",
        help="Output language (default: auto).",
    )
    analyze_parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text).",
    )
    analyze_parser.add_argument(
        "--state-dir",
        type=Path,
        default=None,
        help="State directory for cache and session storage.",
    )
    analyze_parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable cache read and write.",
    )
    analyze_parser.add_argument(
        "--session-id",
        default=None,
        help="Session ID for state tracking.",
    )


def _add_validate_patch_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Add the deterministic Phase 04 patch-validation subcommand."""
    from agent_solution.patch_validation.models import ValidationProfile

    parser = subparsers.add_parser(
        "validate-patch",
        help="Apply one unified patch only in a detached worktree and run allowlisted checks.",
    )
    parser.add_argument("--patch-file", type=Path, required=True, help="UTF-8 unified diff file.")
    parser.add_argument(
        "--repository",
        type=Path,
        default=None,
        help="Repository root. Defaults to current directory.",
    )
    parser.add_argument(
        "--base-ref",
        default="HEAD",
        help="Immutable Git commit/ref for the worktree.",
    )
    parser.add_argument(
        "--profile",
        choices=[profile.value for profile in ValidationProfile],
        default=ValidationProfile.STANDARD.value,
        help="Named fixed command allowlist.",
    )
    parser.add_argument(
        "--allow-path",
        action="append",
        default=[],
        help="Optional exact repository-relative path allowlist. Repeat as needed.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=None,
        help="Directory for the machine-readable validation artifact.",
    )
    parser.add_argument(
        "--retain-worktree",
        action="store_true",
        help="Keep the temporary detached worktree for manual debugging.",
    )


def _add_readiness_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Add the deterministic Phase 05 readiness subcommand."""
    parser = subparsers.add_parser(
        "readiness",
        help="Evaluate readiness only from Phase 03 and Phase 04 JSON artifacts.",
    )
    parser.add_argument(
        "--analysis-artifact",
        type=Path,
        required=True,
        help="Phase 03 structured JSON result.",
    )
    parser.add_argument(
        "--patch-validation-artifact",
        type=Path,
        default=None,
        help="Phase 04 machine-readable validation artifact.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=None,
        help="Directory for the machine-readable readiness artifact.",
    )


def _run_validate_patch(args: argparse.Namespace) -> int:
    """Execute Phase 04 without any model call or source-checkout mutation."""
    from agent_solution.patch_validation.models import PatchValidationStatus, ValidationProfile
    from agent_solution.patch_validation.service import validate_patch, write_validation_artifact

    repository = args.repository.resolve() if args.repository else Path.cwd()
    artifact_dir = args.artifact_dir or repository / "artifacts"
    try:
        patch_text = args.patch_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(json.dumps({"status": "INVALID_REQUEST", "error": str(exc)}, indent=2))
        return 1

    result = validate_patch(
        repository,
        patch_text,
        base_ref=args.base_ref,
        validation_profile=ValidationProfile(args.profile),
        allowed_paths=tuple(args.allow_path),
        retain_worktree=args.retain_worktree,
    )
    artifact_path = write_validation_artifact(result, artifact_dir)
    output = result.to_dict()
    output["artifact_path"] = str(artifact_path)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if result.status is PatchValidationStatus.VALIDATED else 1


def _run_readiness(args: argparse.Namespace) -> int:
    """Execute Phase 05 from prior machine-readable artifacts only."""
    from agent_solution.decision.models import ReadinessStatus
    from agent_solution.decision.policy import (
        evaluate_readiness,
        load_json_artifact,
        write_readiness_artifact,
    )

    try:
        analysis_payload = load_json_artifact(args.analysis_artifact)
        patch_payload = (
            load_json_artifact(args.patch_validation_artifact)
            if args.patch_validation_artifact
            else None
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "INVALID_INPUT", "error": str(exc)}, indent=2))
        return 1

    decision = evaluate_readiness(analysis_payload, patch_payload)
    artifact_dir = args.artifact_dir or args.analysis_artifact.resolve().parent
    artifact_path = write_readiness_artifact(decision, artifact_dir)
    output = decision.to_dict()
    output["artifact_path"] = str(artifact_path)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if decision.status is ReadinessStatus.READY else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="storefront-guard",
        description="Local-first, evidence-based storefront change review prototype.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command")
    status_parser = subparsers.add_parser(
        "status",
        help="Show the current bootstrap status and resolved project root.",
    )
    status_parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Optional explicit project root. Defaults to automatic discovery.",
    )

    _add_analyze_subparser(subparsers)
    _add_validate_patch_subparser(subparsers)
    _add_readiness_subparser(subparsers)
    return parser


def _run_analyze(args: argparse.Namespace) -> int:
    """Execute the analyze command."""
    from agent_solution.analysis.orchestrator import AnalysisOrchestrator
    from agent_solution.analysis.renderer import render_result
    from agent_solution.git_tools.collector import collect_git_context
    from agent_solution.git_tools.models import ScopeMode
    from agent_solution.intake.policy import process_request

    repository = args.repository.resolve() if args.repository else Path.cwd()
    state_dir = args.state_dir

    # Step 1: Run intake
    has_working_tree = False
    has_diff = False
    try:
        from agent_solution.git_tools.collector import _run_git

        result = _run_git(
            ["status", "--porcelain"],
            cwd=repository,
            timeout=10,
        )
        if result.evidence.exit_code == 0 and result.stdout.strip():
            has_working_tree = True
            has_diff = True
    except Exception:  # noqa: BLE001
        pass

    intake = process_request(
        request_id="cli-request",
        text=args.request,
        has_diff=has_diff,
        has_working_tree=has_working_tree,
    )

    # Step 2: Collect Git context (only when allowed)
    git_snapshot = collect_git_context(
        repository_root=repository,
        scope_mode=ScopeMode.WORKING_TREE_DIFF,
        intake_decision=intake.decision.value,
    )

    # Step 3: Run analysis
    orchestrator = AnalysisOrchestrator(
        state_dir=state_dir,
        no_cache=args.no_cache,
    )

    result = orchestrator.analyze(
        intake=intake,
        git_snapshot=git_snapshot,
        repository_root=repository,
        output_language=args.language,
        session_id=args.session_id,
    )

    # Step 4: Render
    output = render_result(result, args.format, args.language)

    if args.format == "json":
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(output)

    # Return non-zero for failures
    if result.status.value in (
        "MODEL_UNAVAILABLE",
        "MODEL_TIMEOUT",
        "MODEL_EXECUTION_FAILED",
        "MODEL_OUTPUT_INVALID",
        "EVIDENCE_VALIDATION_FAILED",
    ):
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "status":
        root = args.project_root.resolve() if args.project_root else project_root()
        print("Storefront Change Guard bootstrap scaffold")
        print(f"Version: {__version__}")
        print(f"Project root: {root}")
        print("Implemented capabilities: Phase 03 evidence-grounded analysis")
        return 0

    if args.command == "analyze":
        return _run_analyze(args)

    if args.command == "validate-patch":
        return _run_validate_patch(args)

    if args.command == "readiness":
        return _run_readiness(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
