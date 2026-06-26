"""Phase 05 readiness-policy tests."""

from __future__ import annotations

import json
from pathlib import Path

from agent_solution.decision.models import ReadinessReasonCode, ReadinessStatus
from agent_solution.decision.policy import (
    evaluate_readiness,
    load_json_artifact,
    write_readiness_artifact,
)


def _analysis(*, status: str = "ANALYSIS_COMPLETED", findings: list[dict] | None = None) -> dict:
    return {
        "status": status,
        "analysis_mode": "CODE_REVIEW",
        "summary": "analysis",
        "findings": findings if findings is not None else [],
        "evidence_bundle_sha256": "abc",
    }


def _validation(*, status: str = "VALIDATED", commands: list[dict] | None = None) -> dict:
    return {
        "status": status,
        "command_results": commands
        if commands is not None
        else [
            {"name": "patch_apply", "exit_code": 0, "timed_out": False},
            {"name": "pytest", "exit_code": 0, "timed_out": False},
        ],
    }


class TestReadinessPolicy:
    """Readiness remains policy-driven and independent of model prose."""

    def test_ready_requires_completed_analysis_and_successful_validation(self) -> None:
        decision = evaluate_readiness(_analysis(), _validation())

        assert decision.status is ReadinessStatus.READY
        assert decision.reasons[0].code is ReadinessReasonCode.ALL_REQUIRED_GATES_PASSED
        assert decision.analysis_artifact_sha256
        assert decision.patch_validation_artifact_sha256

    def test_incomplete_analysis_is_insufficient_evidence(self) -> None:
        decision = evaluate_readiness(_analysis(status="MODEL_OUTPUT_INVALID"), _validation())

        assert decision.status is ReadinessStatus.INSUFFICIENT_EVIDENCE
        assert decision.reasons[0].code is ReadinessReasonCode.ANALYSIS_NOT_COMPLETED

    def test_high_or_critical_finding_blocks_readiness(self) -> None:
        decision = evaluate_readiness(
            _analysis(findings=[{"title": "shipping threshold", "severity": "HIGH"}]),
            _validation(),
        )

        assert decision.status is ReadinessStatus.NOT_READY
        assert decision.reasons[0].code is ReadinessReasonCode.HIGH_OR_CRITICAL_FINDING

    def test_missing_patch_validation_is_insufficient_evidence(self) -> None:
        decision = evaluate_readiness(_analysis(), None)

        assert decision.status is ReadinessStatus.INSUFFICIENT_EVIDENCE
        assert decision.reasons[0].code is ReadinessReasonCode.PATCH_VALIDATION_MISSING

    def test_failed_patch_validation_blocks_readiness(self) -> None:
        decision = evaluate_readiness(_analysis(), _validation(status="VALIDATION_FAILED"))

        assert decision.status is ReadinessStatus.NOT_READY
        assert decision.reasons[0].code is ReadinessReasonCode.PATCH_VALIDATION_NOT_VALIDATED

    def test_failed_validation_command_blocks_readiness(self) -> None:
        decision = evaluate_readiness(
            _analysis(),
            _validation(commands=[{"name": "pytest", "exit_code": 1, "timed_out": False}]),
        )

        assert decision.status is ReadinessStatus.NOT_READY
        assert decision.reasons[0].code is ReadinessReasonCode.PATCH_VALIDATION_COMMAND_FAILED

    def test_artifact_round_trip(self, tmp_path: Path) -> None:
        decision = evaluate_readiness(_analysis(), _validation())
        artifact = write_readiness_artifact(decision, tmp_path)
        loaded = load_json_artifact(artifact)

        assert artifact.exists()
        assert loaded["status"] == "READY"
        assert loaded["policy_version"]
        assert loaded["reasons"][0]["code"] == "ALL_REQUIRED_GATES_PASSED"
        assert json.loads(artifact.read_text(encoding="utf-8")) == loaded
