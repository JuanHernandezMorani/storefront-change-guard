"""Evidence-grounded semantic analysis models.

All Phase 03 analysis decisions are encoded as explicit enum values and
frozen dataclasses.  Prose is never the sole carrier of analysis claims.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class AnalysisStatus(StrEnum):
    """Explicit outcome status for analysis execution."""

    ANALYSIS_COMPLETED = "ANALYSIS_COMPLETED"
    ANALYSIS_CACHE_HIT = "ANALYSIS_CACHE_HIT"
    INTAKE_BLOCKED = "INTAKE_BLOCKED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    MODEL_TIMEOUT = "MODEL_TIMEOUT"
    MODEL_EXECUTION_FAILED = "MODEL_EXECUTION_FAILED"
    MODEL_OUTPUT_INVALID = "MODEL_OUTPUT_INVALID"
    EVIDENCE_VALIDATION_FAILED = "EVIDENCE_VALIDATION_FAILED"
    PHASE_AUTHORITY_LIMIT = "PHASE_AUTHORITY_LIMIT"


class ClaimStatus(StrEnum):
    """Exactly one of these must be assigned to every claim."""

    VERIFIED = "VERIFIED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


class Severity(StrEnum):
    """Finding severity classification."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class AnalysisMode(StrEnum):
    """Analysis modes supported by Phase 03."""

    CODE_REVIEW = "CODE_REVIEW"
    CODEBASE_QUESTION = "CODEBASE_QUESTION"
    BUG_DIAGNOSIS = "BUG_DIAGNOSIS"
    PATCH_PROPOSAL = "PATCH_PROPOSAL"
    READINESS_ASSESSMENT = "READINESS_ASSESSMENT"


class SourceKind(StrEnum):
    """How an evidence record was sourced."""

    DIFF_ARTIFACT = "diff_artifact"
    FILE_EXCERPT = "file_excerpt"
    SEARCH_RESULT = "search_result"
    EXPLICIT_PATH = "explicit_path"


# ---------------------------------------------------------------------------
# Evidence records
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """A single bounded evidence record."""

    evidence_id: str
    source_kind: SourceKind
    relative_path: str
    start_line: int
    end_line: int
    content: str
    content_sha256: str
    byte_count: int
    selection_reason: str
    provenance: str


@dataclass(frozen=True, slots=True)
class EvidenceBundle:
    """Complete bounded evidence bundle for analysis."""

    analysis_request_id: str
    intake_request_id: str
    repository_fingerprint: str
    repository_fingerprint_complete_for_cache: bool
    task_type: str
    requested_output_language: str
    evidence_bundle_schema_version: str
    evidence_records: tuple[EvidenceRecord, ...]
    excluded_evidence_records: tuple[EvidenceRecord, ...]
    bundle_byte_count: int
    bundle_sha256: str
    collection_limitations: tuple[str, ...]
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


# ---------------------------------------------------------------------------
# Claims and findings
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Claim:
    """A structured claim with status and evidence references."""

    claim_id: str
    text: str
    claim_status: ClaimStatus
    evidence_ids: tuple[str, ...] = ()
    inference_basis: str | None = None
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AnalysisFinding:
    """A code review finding with severity and evidence."""

    title: str
    severity: Severity
    claim_ids: tuple[str, ...] = ()
    description: str = ""
    impact: str = ""
    recommendation: str = ""
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AnalysisRecommendation:
    """A recommended next safe action."""

    action: str
    rationale: str = ""
    evidence_ids: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Analysis request and result
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class GroundedAnalysisRequest:
    """Request for grounded analysis."""

    analysis_request_id: str
    intake_request_id: str
    analysis_mode: AnalysisMode
    original_request: str
    normalized_request: str
    output_language: str
    evidence_bundle: EvidenceBundle
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


@dataclass(frozen=True, slots=True)
class GroundedAnalysisResult:
    """Complete validated analysis result."""

    analysis_request_id: str
    intake_request_id: str
    status: AnalysisStatus
    analysis_mode: AnalysisMode
    summary: str
    claims: tuple[Claim, ...] = ()
    findings: tuple[AnalysisFinding, ...] = ()
    recommendations: tuple[AnalysisRecommendation, ...] = ()
    next_safe_action: str = ""
    phase_limitations: tuple[str, ...] = ()
    evidence_bundle_sha256: str = ""
    model_id: str = ""
    runtime_profile_version: str = ""
    prompt_schema_version: str = ""
    cache_hit: bool = False
    output_language: str = "en"
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )


# ---------------------------------------------------------------------------
# Model runtime configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class SingleModelRuntimeConfig:
    """Configuration for the single local model runtime.

    Reconciled with Test 1 successful profile evidence.
    """

    model_id: str
    model_filename: str
    model_path: str
    runtime_backend: str
    runtime_executable_path: str
    runtime_executable_name: str
    context_limit: int
    completion_limit: int
    timeout_seconds: int
    thread_count: int
    thread_batch_count: int = 12
    batch_size: int = 1024
    micro_batch_size: int = 512
    temperature: float = 0.0
    top_p: float = 1.0
    min_p: float = 0.1
    repeat_penalty: float = 1.0
    flash_attention_enabled: bool = True
    kv_cache_type_k: str = "q8_0"
    kv_cache_type_v: str = "q8_0"
    gpu_layers: str = "auto"
    priority: int = 3
    prompt_schema_version: str = "0.3.1"
    runtime_profile_version: str = "0.3.1"


@dataclass(frozen=True, slots=True)
class ModelExecutionResult:
    """Result from a single model invocation."""

    success: bool
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    duration_ms: int
    command: tuple[str, ...] = ()
    error_message: str = ""
    raw_stdout_byte_count: int = 0
    stdout_sanitization_categories: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Collection limits for Phase 3
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Phase3Limits:
    """Configurable bounds for Phase 3 evidence and execution."""

    max_evidence_records: int = 8
    max_total_evidence_bytes: int = 81920
    max_single_evidence_bytes: int = 32768
    max_search_queries: int = 3
    max_search_results: int = 20
    max_model_invocations_per_request: int = 1
    max_evidence_expansion_passes: int = 1
    max_model_output_bytes: int = 131072
    max_session_updates_per_request: int = 1


# ---------------------------------------------------------------------------
# Cache key
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class AnalysisCacheKey:
    """Deterministic cache key for analysis results."""

    normalized_request_sha256: str
    task_type: str
    output_language: str
    model_id: str
    runtime_profile_version: str
    prompt_schema_version: str
    repository_fingerprint: str
    evidence_bundle_sha256: str
    claim_policy_version: str


# ---------------------------------------------------------------------------
# Envelope diagnostics
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ModelEnvelopeDiagnostics:
    """Diagnostics for reasoning-aware output envelope extraction."""

    raw_output_byte_count: int
    reasoning_block_detected: bool
    reasoning_block_byte_count: int
    reasoning_block_closed: bool
    final_json_detected: bool
    json_parse_status: str
    schema_validation_status: str
    failure_category: str | None
