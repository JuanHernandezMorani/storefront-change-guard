"""Safe-default resolver.

Determines whether conservative defaults may be applied to a request.
Every default is recorded and must be visible in the execution contract.
"""

from __future__ import annotations

from agent_solution.intake.models import (
    Assumption,
    ConfidenceLevel,
    SafeDefaults,
    TaskType,
)


def resolve_safe_defaults(
    task_type: TaskType,
    text: str,
    *,
    has_diff: bool = False,
    has_working_tree: bool = False,
    has_paths: bool = False,
) -> tuple[SafeDefaults, tuple[Assumption, ...]]:
    """Return safe defaults and assumptions for a request, or no-ops.

    Only LOW-risk scenarios are eligible.  Caller must verify risk level
    before calling this function.
    """
    if task_type == TaskType.CODE_REVIEW:
        return _review_defaults(text, has_diff, has_working_tree, has_paths)
    if task_type == TaskType.CODEBASE_QUESTION:
        return _codebase_question_defaults(text)
    if task_type == TaskType.BUG_DIAGNOSIS:
        return _bug_diagnosis_defaults(text, has_paths)
    if task_type == TaskType.READINESS_ASSESSMENT:
        return _readiness_defaults(text)
    if task_type == TaskType.PATCH_PROPOSAL:
        return _patch_defaults(text)
    return SafeDefaults(), ()


def _review_defaults(
    text: str,
    has_diff: bool,
    has_working_tree: bool,
    has_paths: bool = False,
) -> tuple[SafeDefaults, tuple[Assumption, ...]]:
    if has_diff and has_working_tree:
        defaults = SafeDefaults(
            applied=True,
            scope_source="current_git_diff",
            scope_description="The current working-tree diff (staged + unstaged changes).",
            rationale=(
                "The user asked to review the current change and a diff exists. "
                "Defaulting scope to the working-tree diff."
            ),
        )
        assumptions = (
            Assumption(
                field="scope",
                value="current_git_diff",
                confidence=ConfidenceLevel.HIGH,
            ),
            Assumption(
                field="review_depth",
                value="standard",
                confidence=ConfidenceLevel.MEDIUM,
            ),
        )
        return defaults, assumptions

    if has_paths:
        defaults = SafeDefaults(
            applied=True,
            scope_source="explicit_file_paths",
            scope_description="Bounded review scoped to explicit file paths.",
            rationale=(
                "The user requested a review of specific files without a diff. "
                "Defaulting scope to the provided file paths."
            ),
        )
        assumptions = (
            Assumption(
                field="scope",
                value="explicit_file_paths",
                confidence=ConfidenceLevel.MEDIUM,
            ),
            Assumption(
                field="review_depth",
                value="standard",
                confidence=ConfidenceLevel.MEDIUM,
            ),
        )
        return defaults, assumptions

    defaults = SafeDefaults(
        applied=False,
        scope_source="none",
        scope_description="No diff available; cannot apply safe default.",
        rationale="No working-tree diff exists. Safe default not applicable.",
    )
    return defaults, ()


def _codebase_question_defaults(
    text: str,
) -> tuple[SafeDefaults, tuple[Assumption, ...]]:
    defaults = SafeDefaults(
        applied=True,
        scope_source="bounded_repository_search",
        scope_description="Bounded search across repository source files.",
        rationale=(
            "The user asked a codebase question without specifying a path. "
            "Defaulting to bounded repository search."
        ),
    )
    assumptions = (
        Assumption(
            field="scope",
            value="bounded_repository_search",
            confidence=ConfidenceLevel.MEDIUM,
        ),
        Assumption(
            field="search_limit",
            value="max_search_results",
            confidence=ConfidenceLevel.MEDIUM,
        ),
    )
    return defaults, assumptions


def _bug_diagnosis_defaults(
    text: str,
    has_paths: bool = False,
) -> tuple[SafeDefaults, tuple[Assumption, ...]]:
    if has_paths:
        defaults = SafeDefaults(
            applied=True,
            scope_source="explicit_file_paths",
            scope_description="Bounded defect discovery scoped to explicit file paths.",
            rationale=(
                "The user requested bounded defect discovery of specific files. "
                "Defaulting scope to the provided file paths."
            ),
        )
        assumptions = (
            Assumption(
                field="scope",
                value="explicit_file_paths",
                confidence=ConfidenceLevel.MEDIUM,
            ),
            Assumption(
                field="discovery_depth",
                value="bounded_file_analysis",
                confidence=ConfidenceLevel.MEDIUM,
            ),
        )
        return defaults, assumptions

    defaults = SafeDefaults(
        applied=False,
        scope_source="none",
        scope_description="Insufficient information for safe defaults.",
        rationale=(
            "Bug diagnosis requires observed symptoms, error logs, reproduction "
            "steps, or expected-vs-actual behavior. Safe defaults not applicable."
        ),
    )
    return defaults, ()


def _readiness_defaults(
    text: str,
) -> tuple[SafeDefaults, tuple[Assumption, ...]]:
    defaults = SafeDefaults(
        applied=False,
        scope_source="none",
        scope_description="Cannot default readiness assessment.",
        rationale=(
            "Readiness assessment requires explicit deployment target, "
            "validation criteria, and risk tolerance."
        ),
    )
    return defaults, ()


def _patch_defaults(
    text: str,
) -> tuple[SafeDefaults, tuple[Assumption, ...]]:
    defaults = SafeDefaults(
        applied=False,
        scope_source="none",
        scope_description="Cannot default patch proposal.",
        rationale=(
            "Patch proposal requires explicit target area and acceptance criteria."
        ),
    )
    return defaults, (
        Assumption(
            field="application_method",
            value="isolated_worktree_only",
            confidence=ConfidenceLevel.HIGH,
        ),
    )
