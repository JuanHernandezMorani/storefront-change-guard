"""Deterministic Phase 05 readiness-decision data contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ReadinessStatus(StrEnum):
    """Terminal policy decision; never inferred from prose."""

    READY = "READY"
    NOT_READY = "NOT_READY"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    INVALID_INPUT = "INVALID_INPUT"


class ReadinessReasonCode(StrEnum):
    """Stable reasons used by the deterministic readiness policy."""

    ANALYSIS_NOT_COMPLETED = "ANALYSIS_NOT_COMPLETED"
    ANALYSIS_ARTIFACT_INVALID = "ANALYSIS_ARTIFACT_INVALID"
    HIGH_OR_CRITICAL_FINDING = "HIGH_OR_CRITICAL_FINDING"
    PATCH_VALIDATION_MISSING = "PATCH_VALIDATION_MISSING"
    PATCH_VALIDATION_NOT_VALIDATED = "PATCH_VALIDATION_NOT_VALIDATED"
    PATCH_VALIDATION_COMMAND_FAILED = "PATCH_VALIDATION_COMMAND_FAILED"
    ALL_REQUIRED_GATES_PASSED = "ALL_REQUIRED_GATES_PASSED"


@dataclass(frozen=True, slots=True)
class ReadinessReason:
    """A concise policy reason tied to an artifact field or command."""

    code: ReadinessReasonCode
    detail: str


@dataclass(frozen=True, slots=True)
class ReadinessDecision:
    """Machine-readable Phase 05 readiness output."""

    decision_id: str
    status: ReadinessStatus
    policy_version: str
    analysis_artifact_sha256: str
    patch_validation_artifact_sha256: str | None
    reasons: tuple[ReadinessReason, ...]
    created_at_utc: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["reasons"] = [
            {"code": reason.code.value, "detail": reason.detail} for reason in self.reasons
        ]
        return data
