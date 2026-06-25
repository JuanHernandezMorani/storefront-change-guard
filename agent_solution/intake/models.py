"""Request intake models and typed schemas.

All intake decisions are encoded as explicit enum values and frozen
dataclasses.  Prose is never the sole carrier of policy decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class TaskType(StrEnum):
    """Conservatively classified task types for incoming requests."""

    CODE_REVIEW = "CODE_REVIEW"
    BUG_DIAGNOSIS = "BUG_DIAGNOSIS"
    CODEBASE_QUESTION = "CODEBASE_QUESTION"
    READINESS_ASSESSMENT = "READINESS_ASSESSMENT"
    PATCH_PROPOSAL = "PATCH_PROPOSAL"
    UNKNOWN = "UNKNOWN"


class IntakeDecision(StrEnum):
    """Exactly one of these must be returned by the intake gate."""

    ACCEPT_AS_IS = "ACCEPT_AS_IS"
    ACCEPT_WITH_SAFE_DEFAULTS = "ACCEPT_WITH_SAFE_DEFAULTS"
    REFINE_FOR_EXECUTION = "REFINE_FOR_EXECUTION"
    CLARIFY = "CLARIFY"
    REJECT_UNSAFE_OR_UNSUPPORTED = "REJECT_UNSAFE_OR_UNSUPPORTED"


class RiskLevel(StrEnum):
    """Risk classification for a request."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ConfidenceLevel(StrEnum):
    """Classification confidence indicator."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# ---------------------------------------------------------------------------
# Execution contract sub-structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ResolvedScope:
    """Deterministic scope resolved from the request and repository state."""

    description: str
    paths: tuple[str, ...] = ()
    diff_available: bool = False
    search_bounded: bool = False
    search_limit: int = 0


@dataclass(frozen=True, slots=True)
class SafeDefaults:
    """Defaults applied only when risk is LOW and conditions are met."""

    applied: bool = False
    scope_source: str = ""
    scope_description: str = ""
    rationale: str = ""


@dataclass(frozen=True, slots=True)
class Assumption:
    """An explicit assumption recorded during intake processing."""

    field: str
    value: str
    confidence: ConfidenceLevel


@dataclass(frozen=True, slots=True)
class EvidenceRequirement:
    """What evidence is needed to satisfy the request."""

    description: str
    required: bool = True
    available: bool = False


@dataclass(frozen=True, slots=True)
class ExpectedOutputContract:
    """Contractual description of what the output must contain."""

    format: str = ""
    sections: tuple[str, ...] = ()
    must_preserve_original: bool = True


@dataclass(frozen=True, slots=True)
class ClarifyingQuestion:
    """A targeted, minimal question to resolve underspecification."""

    question: str
    reason: str
    priority: int = 1


# ---------------------------------------------------------------------------
# Top-level intake contract
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class IntakeContract:
    """Complete typed output of the request intake gate.

    This is the authoritative decision record for every incoming request.
    """

    request_id: str
    original_request: str
    normalized_request: str
    detected_task_type: TaskType
    decision: IntakeDecision
    confidence: ConfidenceLevel
    resolved_scope: ResolvedScope
    safe_defaults: SafeDefaults
    assumptions: tuple[Assumption, ...] = ()
    missing_information: tuple[str, ...] = ()
    clarifying_questions: tuple[ClarifyingQuestion, ...] = ()
    risk_level: RiskLevel = RiskLevel.LOW
    evidence_requirements: tuple[EvidenceRequirement, ...] = ()
    expected_output_contract: ExpectedOutputContract = field(
        default_factory=ExpectedOutputContract
    )
    blocking_reasons: tuple[str, ...] = ()
    policy_version: str = "0.2.0"
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


# ---------------------------------------------------------------------------
# Refined execution brief
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ExecutionBrief:
    """Structured reformulation produced by REFINE_FOR_EXECUTION.

    Always preserves the original request and lists all assumptions.
    """

    goal: str
    task_type: TaskType
    scope: str
    available_evidence: tuple[str, ...] = ()
    required_evidence: tuple[str, ...] = ()
    safe_defaults: SafeDefaults = field(default_factory=SafeDefaults)
    assumptions: tuple[Assumption, ...] = ()
    constraints: tuple[str, ...] = ()
    expected_output: str = ""
    validation_plan: tuple[str, ...] = ()
    stop_conditions: tuple[str, ...] = ()
    original_request: str = ""


# ---------------------------------------------------------------------------
# Model-profile contract (model-agnostic, for later routing)
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ModelProfile:
    """Model-agnostic configuration contract for future routing.

    Final values must NOT be set based on benchmark assumptions.
    Use placeholders or clearly marked provisional values.
    """

    profile_id: str
    model_id: str = ""
    role: str = ""
    context_limit: int = 0
    default_completion_budget: int = 0
    max_completion_budget: int = 0
    timeout_seconds: int = 0
    supports_structured_output: bool = False
    supports_bilingual_responses: bool = False
    allowed_task_types: tuple[TaskType, ...] = field(
        default_factory=lambda: tuple(TaskType)
    )
    escalation_target: str = ""
    enabled: bool = True


@dataclass(frozen=True, slots=True)
class CacheKey:
    """Cache key for model output deduplication.

    Includes all fields that could affect model output.
    """

    model_id: str = ""
    model_profile_version: str = ""
    prompt_schema_version: str = ""
    output_language: str = ""
    repository_fingerprint: str = ""


# ---------------------------------------------------------------------------
# Intake configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class IntakeConfig:
    """Configuration for the intake gate. Model-agnostic."""

    policy_version: str = "0.2.0"
    prompt_schema_version: str = "0.1.0"
    max_search_results: int = 20
    max_search_context_chars: int = 24000
    allowed_risk_levels: tuple[RiskLevel, ...] = (
        RiskLevel.LOW,
        RiskLevel.MEDIUM,
    )
    reject_on_risk_above: RiskLevel = RiskLevel.HIGH
