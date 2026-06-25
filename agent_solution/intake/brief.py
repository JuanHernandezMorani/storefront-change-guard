"""Refined execution-brief builder.

Constructs a structured execution brief that preserves the original
request wording and lists all assumptions.  Never claims that
refinement makes an ambiguous request certain.
"""

from __future__ import annotations

from agent_solution.intake.models import (
    Assumption,
    ConfidenceLevel,
    ExecutionBrief,
    IntakeDecision,
    ResolvedScope,
    SafeDefaults,
    TaskType,
)


def build_execution_brief(
    *,
    original_request: str,
    task_type: TaskType,
    decision: IntakeDecision,
    resolved_scope: ResolvedScope,
    safe_defaults: SafeDefaults,
    assumptions: tuple[Assumption, ...],
    confidence: ConfidenceLevel,
) -> ExecutionBrief:
    """Build a refined execution brief from intake results.

    Only called when decision is ACCEPT_AS_IS, ACCEPT_WITH_SAFE_DEFAULTS,
    or REFINE_FOR_EXECUTION.  Never for CLARIFY or REJECT.
    """
    goal = _derive_goal(original_request, task_type)
    scope = _derive_scope(resolved_scope, task_type)
    constraints = _derive_constraints(task_type, decision)
    expected_output = _derive_expected_output(task_type, confidence)
    validation_plan = _derive_validation_plan(task_type, decision)
    stop_conditions = _derive_stop_conditions(task_type)

    available_evidence: list[str] = []
    if resolved_scope.diff_available:
        available_evidence.append("current_working_tree_diff")
    if resolved_scope.paths:
        available_evidence.append("explicit_file_paths")

    required_evidence: list[str] = []
    if task_type == TaskType.BUG_DIAGNOSIS:
        required_evidence.extend([
            "observed_symptom",
            "expected_behavior",
        ])
    elif task_type == TaskType.READINESS_ASSESSMENT:
        required_evidence.extend([
            "deployment_target",
            "validation_criteria",
        ])
    elif task_type == TaskType.PATCH_PROPOSAL:
        required_evidence.extend([
            "target_files",
            "acceptance_criteria",
        ])

    return ExecutionBrief(
        goal=goal,
        task_type=task_type,
        scope=scope,
        available_evidence=tuple(available_evidence),
        required_evidence=tuple(required_evidence),
        safe_defaults=safe_defaults,
        assumptions=assumptions,
        constraints=constraints,
        expected_output=expected_output,
        validation_plan=validation_plan,
        stop_conditions=stop_conditions,
        original_request=original_request,
    )


def _derive_goal(original: str, task_type: TaskType) -> str:
    prefixes = {
        TaskType.CODE_REVIEW: "Review",
        TaskType.BUG_DIAGNOSIS: "Diagnose",
        TaskType.CODEBASE_QUESTION: "Answer",
        TaskType.READINESS_ASSESSMENT: "Assess readiness",
        TaskType.PATCH_PROPOSAL: "Propose patch",
        TaskType.UNKNOWN: "Process",
    }
    prefix = prefixes.get(task_type, "Process")
    return f"{prefix}: {original.strip()}"


def _derive_scope(scope: ResolvedScope, task_type: TaskType) -> str:
    if scope.description:
        return scope.description
    return "To be determined from repository context."


def _derive_constraints(
    task_type: TaskType, decision: IntakeDecision
) -> tuple[str, ...]:
    constraints: list[str] = [
        "No autonomous commits, merges, or pushes.",
        "No arbitrary model-generated shell commands.",
    ]
    if decision == IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS:
        constraints.append("Only documented safe defaults are applied.")
    if task_type == TaskType.PATCH_PROPOSAL:
        constraints.append("Patches apply only in temporary worktrees.")
    if task_type == TaskType.READINESS_ASSESSMENT:
        constraints.append("Readiness requires explicit validation criteria.")
    return tuple(constraints)


def _derive_expected_output(task_type: TaskType, confidence: ConfidenceLevel) -> str:
    outputs = {
        TaskType.CODE_REVIEW: "Structured review with findings, severities, and evidence.",
        TaskType.BUG_DIAGNOSIS: "Root-cause hypothesis with supporting evidence.",
        TaskType.CODEBASE_QUESTION: "Answer with file references and line numbers.",
        TaskType.READINESS_ASSESSMENT: "Readiness decision with gap analysis.",
        TaskType.PATCH_PROPOSAL: "Diff-based proposal with validation worktree results.",
        TaskType.UNKNOWN: "Best-effort analysis with explicit uncertainty.",
    }
    base = outputs.get(task_type, "Analysis result.")
    if confidence == ConfidenceLevel.LOW:
        base += " Explicit uncertainty markers required."
    return base


def _derive_validation_plan(
    task_type: TaskType, decision: IntakeDecision
) -> tuple[str, ...]:
    plan: list[str] = []
    if task_type in (TaskType.CODE_REVIEW, TaskType.PATCH_PROPOSAL):
        plan.append("Verify findings against repository source files.")
        plan.append("Check that no unvalidated claims remain in output.")
    if task_type == TaskType.BUG_DIAGNOSIS:
        plan.append("Validate that each hypothesis maps to observable evidence.")
    if task_type == TaskType.READINESS_ASSESSMENT:
        plan.append("Verify all readiness criteria are explicitly defined.")
    return tuple(plan)


def _derive_stop_conditions(task_type: TaskType) -> tuple[str, ...]:
    conditions: list[str] = [
        "Evidence cannot be verified against repository files.",
        "Confidence drops below threshold for reported findings.",
    ]
    if task_type == TaskType.PATCH_PROPOSAL:
        conditions.append("Patch modifies files outside declared scope.")
    if task_type == TaskType.READINESS_ASSESSMENT:
        conditions.append("Deployment target or criteria remain undefined.")
    return tuple(conditions)
