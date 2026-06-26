"""Deterministic validator and policy engine.

Orchestrates the intake pipeline: classification, validation,
scope resolution, safe-default application, clarification generation,
and execution-brief construction.  Fully deterministic; no model calls.
"""

from __future__ import annotations

import re

from agent_solution.intake.clarifier import generate_clarifications
from agent_solution.intake.classifier import classify_request, extract_file_targets
from agent_solution.intake.defaults import resolve_safe_defaults
from agent_solution.intake.models import (
    ConfidenceLevel,
    EvidenceRequirement,
    ExpectedOutputContract,
    IntakeConfig,
    IntakeContract,
    IntakeDecision,
    ResolvedScope,
    RiskLevel,
    SafeDefaults,
    TaskType,
)

# ---------------------------------------------------------------------------
# Constraint phrases that must NOT trigger task signals
# ---------------------------------------------------------------------------

_CONSTRAINT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bdo not\b.*\bmodify\b", re.IGNORECASE),
    re.compile(r"\bdon't\b.*\bmodify\b", re.IGNORECASE),
    re.compile(r"\bdo not\b.*\bchange\b", re.IGNORECASE),
    re.compile(r"\bdon't\b.*\bchange\b", re.IGNORECASE),
    re.compile(r"\bwithout modifying\b", re.IGNORECASE),
    re.compile(r"\bwithout changing\b", re.IGNORECASE),
    re.compile(r"\bwithout applying\b", re.IGNORECASE),
    re.compile(r"\bwithout running\b", re.IGNORECASE),
    re.compile(r"\bdo not apply a patch\b", re.IGNORECASE),
    re.compile(r"\bdon't apply a patch\b", re.IGNORECASE),
    re.compile(r"\bdo not apply\b", re.IGNORECASE),
    re.compile(r"\bdon't apply\b", re.IGNORECASE),
    re.compile(r"\bno modifiques\b", re.IGNORECASE),
    re.compile(r"\bno modificar\b", re.IGNORECASE),
    re.compile(r"\bno cambies\b", re.IGNORECASE),
    re.compile(r"\bno apliques\b", re.IGNORECASE),
    re.compile(r"\bno ejecutes\b", re.IGNORECASE),
    re.compile(r"\bno corras\b", re.IGNORECASE),
    re.compile(r"\boutput json\b", re.IGNORECASE),
    re.compile(r"\breturn the answer in spanish\b", re.IGNORECASE),
    re.compile(r"\breturn the answer in english\b", re.IGNORECASE),
    re.compile(r"\bscope to\b", re.IGNORECASE),
]


def _remove_constraint_phrases(text: str) -> str:
    """Remove constraint phrases that should not trigger task signals."""
    result = text
    for pat in _CONSTRAINT_PATTERNS:
        result = pat.sub('', result)
    return result


def _assess_risk(
    task_type: TaskType,
    text: str,
    *,
    has_diff: bool,
    has_paths: bool,
    missing_evidence: bool,
) -> RiskLevel:
    """Assess risk level deterministically.

    BUG_DIAGNOSIS and READINESS_ASSESSMENT with missing evidence are
    elevated to MEDIUM or HIGH.  CODE_REVIEW with a diff is LOW.
    Bounded defect discovery (has_paths) is treated as LOW risk.
    """
    if task_type == TaskType.BUG_DIAGNOSIS:
        if has_paths:
            return RiskLevel.LOW
        if missing_evidence:
            return RiskLevel.HIGH
        return RiskLevel.MEDIUM
    if task_type == TaskType.READINESS_ASSESSMENT:
        if missing_evidence:
            return RiskLevel.HIGH
        return RiskLevel.MEDIUM
    if task_type == TaskType.PATCH_PROPOSAL:
        return RiskLevel.MEDIUM
    if task_type == TaskType.CODE_REVIEW:
        if has_diff:
            return RiskLevel.LOW
        return RiskLevel.MEDIUM
    if task_type == TaskType.CODEBASE_QUESTION:
        return RiskLevel.LOW
    return RiskLevel.MEDIUM


def _has_mixed_goals(text: str) -> bool:
    """Detect requests mixing materially distinct task signals.

    A request is mixed-goals when it contains signals from two or more
    distinct task types that require different execution contracts or
    levels of authority.  Deterministic signal-overlap approach.

    Constraint phrases (e.g. "do not modify files", "only",
    "return the answer in Spanish") are stripped before detection
    so they do not create false extra-task signals.
    """
    from agent_solution.intake.classifier import (
        _BUG_PATTERNS,
        _CODEBASE_Q_PATTERNS,
        _PATCH_PATTERNS,
        _READINESS_PATTERNS,
        _REVIEW_PATTERNS,
        _count_matches,
    )

    clean_text = _remove_constraint_phrases(text)

    task_signals: set[TaskType] = set()
    threshold = 1

    if _count_matches(clean_text, _REVIEW_PATTERNS) >= threshold:
        task_signals.add(TaskType.CODE_REVIEW)
    if _count_matches(clean_text, _BUG_PATTERNS) >= threshold:
        task_signals.add(TaskType.BUG_DIAGNOSIS)
    if _count_matches(clean_text, _CODEBASE_Q_PATTERNS) >= threshold:
        task_signals.add(TaskType.CODEBASE_QUESTION)
    if _count_matches(clean_text, _READINESS_PATTERNS) >= threshold:
        task_signals.add(TaskType.READINESS_ASSESSMENT)
    if _count_matches(clean_text, _PATCH_PATTERNS) >= threshold:
        task_signals.add(TaskType.PATCH_PROPOSAL)

    return len(task_signals) >= 2


def _missing_evidence_for_type(
    task_type: TaskType,
    text: str,
    *,
    has_diff: bool,
    has_error_info: bool,
    has_paths: bool,
    has_validation_criteria: bool,
    has_target_env: bool,
) -> tuple[bool, ...]:
    """Determine which evidence categories are missing for the task type."""
    missing_error = False
    missing_paths = False
    missing_validation = False
    missing_env = False

    if task_type == TaskType.BUG_DIAGNOSIS:
        missing_error = not has_error_info
    elif task_type == TaskType.CODE_REVIEW:
        missing_paths = not has_diff and not has_paths
    elif task_type == TaskType.READINESS_ASSESSMENT:
        missing_validation = not has_validation_criteria
        missing_env = not has_target_env
    elif task_type == TaskType.PATCH_PROPOSAL:
        missing_paths = not has_paths

    return missing_error, missing_paths, missing_validation, missing_env


def _evidence_requirements(
    task_type: TaskType,
    has_diff: bool,
    has_paths: bool,
) -> tuple[EvidenceRequirement, ...]:
    """Build evidence requirements for the task type."""
    reqs: list[EvidenceRequirement] = []

    if task_type == TaskType.CODE_REVIEW:
        reqs.append(
            EvidenceRequirement(
                description="Working-tree diff or explicit file paths",
                required=True,
                available=has_diff or has_paths,
            )
        )
    elif task_type == TaskType.BUG_DIAGNOSIS:
        reqs.append(
            EvidenceRequirement(
                description="Observed symptom or error information",
                required=True,
                available=False,
            )
        )
    elif task_type == TaskType.READINESS_ASSESSMENT:
        reqs.append(
            EvidenceRequirement(
                description="Target deployment environment",
                required=True,
                available=False,
            )
        )
        reqs.append(
            EvidenceRequirement(
                description="Validation criteria",
                required=True,
                available=False,
            )
        )
    elif task_type == TaskType.PATCH_PROPOSAL:
        reqs.append(
            EvidenceRequirement(
                description="Target files or behavior to change",
                required=True,
                available=has_paths,
            )
        )
        reqs.append(
            EvidenceRequirement(
                description="Acceptance criteria",
                required=True,
                available=False,
            )
        )

    return tuple(reqs)


def _expected_output_contract(
    task_type: TaskType,
) -> ExpectedOutputContract:
    """Build the expected output contract for the task type."""
    if task_type == TaskType.CODE_REVIEW:
        return ExpectedOutputContract(
            format="markdown",
            sections=("findings", "severity", "evidence", "recommendation"),
            must_preserve_original=True,
        )
    if task_type == TaskType.BUG_DIAGNOSIS:
        return ExpectedOutputContract(
            format="markdown",
            sections=("hypothesis", "evidence", "confidence", "next_steps"),
            must_preserve_original=True,
        )
    if task_type == TaskType.CODEBASE_QUESTION:
        return ExpectedOutputContract(
            format="markdown",
            sections=("answer", "file_references", "line_numbers"),
            must_preserve_original=True,
        )
    if task_type == TaskType.READINESS_ASSESSMENT:
        return ExpectedOutputContract(
            format="markdown",
            sections=("decision", "gaps", "conditions", "next_steps"),
            must_preserve_original=True,
        )
    if task_type == TaskType.PATCH_PROPOSAL:
        return ExpectedOutputContract(
            format="diff",
            sections=("target_files", "changes", "validation", "rollback"),
            must_preserve_original=True,
        )
    return ExpectedOutputContract(
        format="markdown",
        sections=("analysis", "uncertainty"),
        must_preserve_original=True,
    )


def process_request(
    request_id: str,
    text: str,
    *,
    has_diff: bool = False,
    has_working_tree: bool = False,
    has_error_info: bool = False,
    has_paths: bool = False,
    has_validation_criteria: bool = False,
    has_target_env: bool = False,
    config: IntakeConfig | None = None,
) -> IntakeContract:
    """Run the full intake pipeline on a request.

    Returns a complete IntakeContract with the intake decision,
    classification, scope, defaults, assumptions, and any
    clarifying questions.
    """
    if config is None:
        config = IntakeConfig()

    normalized = text.strip()

    # Strip constraint phrases before classification so they do not
    # create false extra-task signals (e.g. "do not modify files"
    # must not trigger PATCH_PROPOSAL).
    clean_text = _remove_constraint_phrases(normalized)

    # Extract explicit file targets from request text
    explicit_file_targets = extract_file_targets(normalized)
    has_paths = has_paths or bool(explicit_file_targets)

    # --- Step 1: Classify ---
    task_type, confidence = classify_request(clean_text)

    # --- Step 2: Assess risk ---
    missing_error, missing_paths, missing_validation, missing_env = (
        _missing_evidence_for_type(
            task_type,
            normalized,
            has_diff=has_diff,
            has_error_info=has_error_info,
            has_paths=has_paths,
            has_validation_criteria=has_validation_criteria,
            has_target_env=has_target_env,
        )
    )
    any_missing = missing_error or missing_paths or missing_validation or missing_env
    risk_level = _assess_risk(
        task_type,
        normalized,
        has_diff=has_diff,
        has_paths=has_paths,
        missing_evidence=any_missing,
    )

    # --- Step 3: Safety gate ---
    decision = _determine_decision(
        task_type,
        confidence,
        risk_level,
        config,
        has_diff=has_diff,
        has_working_tree=has_working_tree,
        has_paths=has_paths,
        missing_error=missing_error,
        missing_paths=missing_paths,
        missing_validation=missing_validation,
        missing_env=missing_env,
        mixed_goals=_has_mixed_goals(normalized),
    )

    # --- Step 4: Resolve scope and defaults ---
    safe_defaults, assumptions = resolve_safe_defaults(
        task_type,
        normalized,
        has_diff=has_diff,
        has_working_tree=has_working_tree,
        has_paths=has_paths,
    )

    scope = _resolve_scope(
        task_type,
        normalized,
        has_diff=has_diff,
        has_paths=has_paths,
        safe_defaults=safe_defaults,
        explicit_file_targets=explicit_file_targets,
    )

    # --- Step 5: Clarifications (if needed) ---
    clarifying_questions = ()
    if decision in (IntakeDecision.CLARIFY, IntakeDecision.REJECT_UNSAFE_OR_UNSUPPORTED):
        clarifying_questions = generate_clarifications(
            task_type,
            normalized,
            missing_paths=missing_paths,
            missing_error_info=missing_error,
            missing_validation_criteria=missing_validation,
            missing_target_env=missing_env,
            mixed_goals=_has_mixed_goals(normalized),
        )

    # --- Step 6: Evidence requirements ---
    evidence_reqs = _evidence_requirements(task_type, has_diff, has_paths)

    # --- Step 7: Output contract ---
    output_contract = _expected_output_contract(task_type)

    # --- Step 8: Blocking reasons ---
    mixed = _has_mixed_goals(normalized)
    blocking = _blocking_reasons(
        decision,
        risk_level,
        confidence,
        config,
        missing_error=missing_error,
        missing_paths=missing_paths,
        missing_validation=missing_validation,
        missing_env=missing_env,
        mixed_goals=mixed,
    )

    # --- Step 9: Build contract ---
    contract = IntakeContract(
        request_id=request_id,
        original_request=text,
        normalized_request=normalized,
        detected_task_type=task_type,
        decision=decision,
        confidence=confidence,
        resolved_scope=scope,
        safe_defaults=safe_defaults,
        assumptions=assumptions,
        missing_information=_missing_info_list(
            missing_error, missing_paths, missing_validation, missing_env
        ),
        clarifying_questions=clarifying_questions,
        risk_level=risk_level,
        evidence_requirements=evidence_reqs,
        expected_output_contract=output_contract,
        blocking_reasons=blocking,
        policy_version=config.policy_version,
    )

    return contract


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _determine_decision(
    task_type: TaskType,
    confidence: ConfidenceLevel,
    risk_level: RiskLevel,
    config: IntakeConfig,
    *,
    has_diff: bool,
    has_working_tree: bool,
    has_paths: bool,
    missing_error: bool,
    missing_paths: bool,
    missing_validation: bool,
    missing_env: bool,
    mixed_goals: bool,
) -> IntakeDecision:
    """Deterministically choose the intake decision."""
    # Mixed goals: always clarify first (before type-specific logic)
    if mixed_goals:
        return IntakeDecision.CLARIFY

    # Reject unsupported or overly risky
    if risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
        if risk_level == RiskLevel.CRITICAL:
            return IntakeDecision.REJECT_UNSAFE_OR_UNSUPPORTED
        # HIGH risk: clarify unless we have enough evidence
        if missing_error or missing_validation or missing_env:
            return IntakeDecision.CLARIFY

    # UNKNOWN type: clarify
    if task_type == TaskType.UNKNOWN:
        return IntakeDecision.CLARIFY

    # CODE_REVIEW with diff: accept with safe defaults.
    # Concrete evidence (a diff) overrides low classification confidence.
    if task_type == TaskType.CODE_REVIEW:
        if has_diff and has_working_tree:
            return IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        # Bounded file review without diff is safe analysis.
        if has_paths:
            return IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        return IntakeDecision.CLARIFY

    # BUG_DIAGNOSIS: bounded defect discovery of a file is safe analysis.
    if task_type == TaskType.BUG_DIAGNOSIS:
        if has_paths:
            return IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
        if missing_error:
            return IntakeDecision.CLARIFY
        return IntakeDecision.REFINE_FOR_EXECUTION

    # CODEBASE_QUESTION: bounded search is usually safe
    if task_type == TaskType.CODEBASE_QUESTION:
        return IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS

    # Low confidence on remaining types: clarify
    if confidence == ConfidenceLevel.LOW:
        return IntakeDecision.CLARIFY

    # READINESS_ASSESSMENT: needs explicit criteria
    if task_type == TaskType.READINESS_ASSESSMENT:
        if missing_validation or missing_env:
            return IntakeDecision.CLARIFY
        return IntakeDecision.REFINE_FOR_EXECUTION

    # PATCH_PROPOSAL: needs target and criteria
    if task_type == TaskType.PATCH_PROPOSAL:
        if missing_paths:
            return IntakeDecision.CLARIFY
        return IntakeDecision.REFINE_FOR_EXECUTION

    # Fallback
    return IntakeDecision.CLARIFY


def _resolve_scope(
    task_type: TaskType,
    text: str,
    *,
    has_diff: bool,
    has_paths: bool,
    safe_defaults: SafeDefaults,
    explicit_file_targets: tuple[str, ...] = (),
) -> ResolvedScope:
    """Resolve the execution scope from task type and available evidence."""

    if task_type == TaskType.CODE_REVIEW and has_diff:
        return ResolvedScope(
            description="Current working-tree diff.",
            diff_available=True,
            explicit_file_targets=explicit_file_targets,
        )
    if task_type == TaskType.CODE_REVIEW and has_paths:
        return ResolvedScope(
            description="Bounded file review of explicit paths.",
            explicit_file_targets=explicit_file_targets,
        )
    if task_type == TaskType.CODE_REVIEW:
        if explicit_file_targets:
            return ResolvedScope(
                description="Bounded file review of explicit paths.",
                explicit_file_targets=explicit_file_targets,
            )
    if task_type == TaskType.CODEBASE_QUESTION:
        return ResolvedScope(
            description="Bounded repository search.",
            search_bounded=True,
            search_limit=20,
        )
    if task_type == TaskType.BUG_DIAGNOSIS and has_paths:
        return ResolvedScope(
            description="Bounded defect discovery of explicit paths.",
            explicit_file_targets=explicit_file_targets,
        )
    if task_type == TaskType.BUG_DIAGNOSIS and explicit_file_targets:
        return ResolvedScope(
            description="Bounded defect discovery of explicit paths.",
            explicit_file_targets=explicit_file_targets,
        )
    if safe_defaults.applied:
        return ResolvedScope(
            description=safe_defaults.scope_description,
        )
    if task_type == TaskType.PATCH_PROPOSAL and has_paths:
        return ResolvedScope(
            description="Explicit target area from request.",
        )
    return ResolvedScope(
        description="To be determined.",
    )


def _blocking_reasons(
    decision: IntakeDecision,
    risk_level: RiskLevel,
    confidence: ConfidenceLevel,
    config: IntakeConfig,
    *,
    missing_error: bool,
    missing_paths: bool,
    missing_validation: bool,
    missing_env: bool,
    mixed_goals: bool = False,
) -> tuple[str, ...]:
    """List explicit blocking reasons for the decision."""
    reasons: list[str] = []

    if decision == IntakeDecision.REJECT_UNSAFE_OR_UNSUPPORTED:
        reasons.append(f"Risk level {risk_level} exceeds threshold.")
    if decision == IntakeDecision.CLARIFY:
        if mixed_goals:
            reasons.append(
                "Request contains multiple distinct task signals "
                "requiring decomposition into separate requests."
            )
        if missing_error:
            reasons.append("Missing observed symptom or error information.")
        if missing_paths:
            reasons.append("Missing explicit file paths or scope.")
        if missing_validation:
            reasons.append("Missing validation criteria.")
        if missing_env:
            reasons.append("Missing target deployment environment.")
        if confidence == ConfidenceLevel.LOW:
            reasons.append("Classification confidence is insufficient.")
        if risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            reasons.append(f"Risk level {risk_level} requires clarification.")

    return tuple(reasons)


def _missing_info_list(
    missing_error: bool,
    missing_paths: bool,
    missing_validation: bool,
    missing_env: bool,
) -> tuple[str, ...]:
    """Build the missing-information list."""
    info: list[str] = []
    if missing_error:
        info.append("observed_symptom_or_error")
    if missing_paths:
        info.append("explicit_file_paths_or_scope")
    if missing_validation:
        info.append("validation_criteria")
    if missing_env:
        info.append("target_deployment_environment")
    return tuple(info)
