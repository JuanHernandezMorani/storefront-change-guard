"""Phase 05 deterministic readiness policy.

The policy consumes existing Phase 03 and Phase 04 machine-readable artifacts.
It does not call a model, execute arbitrary commands, apply patches, or mutate
repositories.  It only converts already-recorded evidence into a traceable
ready/not-ready decision.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from agent_solution.decision.models import (
    ReadinessDecision,
    ReadinessReason,
    ReadinessReasonCode,
    ReadinessStatus,
)

POLICY_VERSION = "phase-05.1.0"
_COMPLETED_ANALYSIS_STATUSES = {"ANALYSIS_COMPLETED", "ANALYSIS_CACHE_HIT"}


def _canonical_json_sha256(payload: Mapping[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _decision(
    status: ReadinessStatus,
    analysis_payload: Mapping[str, Any],
    patch_payload: Mapping[str, Any] | None,
    reasons: list[ReadinessReason],
) -> ReadinessDecision:
    return ReadinessDecision(
        decision_id=f"phase05-{uuid.uuid4().hex[:12]}",
        status=status,
        policy_version=POLICY_VERSION,
        analysis_artifact_sha256=_canonical_json_sha256(analysis_payload),
        patch_validation_artifact_sha256=(
            _canonical_json_sha256(patch_payload) if patch_payload is not None else None
        ),
        reasons=tuple(reasons),
    )


def evaluate_readiness(
    analysis_payload: Mapping[str, Any],
    patch_validation_payload: Mapping[str, Any] | None,
) -> ReadinessDecision:
    """Apply the explicit readiness policy to Phase 03 and Phase 04 artifacts."""
    if not isinstance(analysis_payload, Mapping):
        return _decision(
            ReadinessStatus.INVALID_INPUT,
            {},
            patch_validation_payload,
            [
                ReadinessReason(
                    ReadinessReasonCode.ANALYSIS_ARTIFACT_INVALID,
                    "Analysis artifact must be a JSON object.",
                )
            ],
        )

    analysis_status = analysis_payload.get("status")
    incomplete_analysis_detail = (
        f"Phase 03 status is {analysis_status!r}; a completed grounded analysis is required."
    )
    if analysis_status not in _COMPLETED_ANALYSIS_STATUSES:
        return _decision(
            ReadinessStatus.INSUFFICIENT_EVIDENCE,
            analysis_payload,
            patch_validation_payload,
            [
                ReadinessReason(
                    ReadinessReasonCode.ANALYSIS_NOT_COMPLETED,
                    incomplete_analysis_detail,
                )
            ],
        )

    findings = analysis_payload.get("findings")
    if not isinstance(findings, list):
        return _decision(
            ReadinessStatus.INVALID_INPUT,
            analysis_payload,
            patch_validation_payload,
            [
                ReadinessReason(
                    ReadinessReasonCode.ANALYSIS_ARTIFACT_INVALID,
                    "Analysis artifact must contain a findings list.",
                )
            ],
        )

    high_or_critical = [
        finding
        for finding in findings
        if isinstance(finding, Mapping) and finding.get("severity") in {"CRITICAL", "HIGH"}
    ]
    if high_or_critical:
        titles = ", ".join(str(finding.get("title", "untitled")) for finding in high_or_critical)
        finding_detail = (
            f"Verified review findings require remediation or an explicit exception: {titles}."
        )
        return _decision(
            ReadinessStatus.NOT_READY,
            analysis_payload,
            patch_validation_payload,
            [
                ReadinessReason(
                    ReadinessReasonCode.HIGH_OR_CRITICAL_FINDING,
                    finding_detail,
                )
            ],
        )

    if patch_validation_payload is None:
        return _decision(
            ReadinessStatus.INSUFFICIENT_EVIDENCE,
            analysis_payload,
            None,
            [
                ReadinessReason(
                    ReadinessReasonCode.PATCH_VALIDATION_MISSING,
                    "Readiness requires a Phase 04 machine-readable patch-validation artifact.",
                )
            ],
        )
    if not isinstance(patch_validation_payload, Mapping):
        return _decision(
            ReadinessStatus.INVALID_INPUT,
            analysis_payload,
            {},
            [
                ReadinessReason(
                    ReadinessReasonCode.PATCH_VALIDATION_NOT_VALIDATED,
                    "Patch-validation artifact must be a JSON object.",
                )
            ],
        )
    patch_status = patch_validation_payload.get("status")
    if patch_status != "VALIDATED":
        patch_not_validated_detail = f"Phase 04 status is {patch_status!r}; expected 'VALIDATED'."
        return _decision(
            ReadinessStatus.NOT_READY,
            analysis_payload,
            patch_validation_payload,
            [
                ReadinessReason(
                    ReadinessReasonCode.PATCH_VALIDATION_NOT_VALIDATED,
                    patch_not_validated_detail,
                )
            ],
        )

    commands = patch_validation_payload.get("command_results")
    if not isinstance(commands, list) or not commands:
        return _decision(
            ReadinessStatus.INSUFFICIENT_EVIDENCE,
            analysis_payload,
            patch_validation_payload,
            [
                ReadinessReason(
                    ReadinessReasonCode.PATCH_VALIDATION_COMMAND_FAILED,
                    "Patch-validation artifact does not contain executed command results.",
                )
            ],
        )
    failed = [
        command
        for command in commands
        if not isinstance(command, Mapping)
        or command.get("exit_code") != 0
        or command.get("timed_out") is True
    ]
    if failed:
        names = ", ".join(
            str(command.get("name", "unknown"))
            for command in failed
            if isinstance(command, Mapping)
        )
        command_failure_detail = (
            f"One or more Phase 04 commands did not pass: {names or 'invalid command record'}."
        )
        return _decision(
            ReadinessStatus.NOT_READY,
            analysis_payload,
            patch_validation_payload,
            [
                ReadinessReason(
                    ReadinessReasonCode.PATCH_VALIDATION_COMMAND_FAILED,
                    command_failure_detail,
                )
            ],
        )

    return _decision(
        ReadinessStatus.READY,
        analysis_payload,
        patch_validation_payload,
        [
            ReadinessReason(
                ReadinessReasonCode.ALL_REQUIRED_GATES_PASSED,
                (
                    "Grounded analysis completed, no HIGH/CRITICAL findings "
                    "remain, and isolated patch validation passed."
                ),
            )
        ],
    )


def load_json_artifact(path: Path) -> dict[str, Any]:
    """Load a JSON object artifact with a deterministic type check."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Artifact is not a JSON object: {path}")
    return payload


def write_readiness_artifact(decision: ReadinessDecision, artifact_dir: Path) -> Path:
    """Write a Phase 05 decision artifact in canonical readable JSON."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    path = artifact_dir / f"{decision.decision_id}.readiness.json"
    path.write_text(
        json.dumps(decision.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path
