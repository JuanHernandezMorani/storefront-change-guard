"""Clarification-question generator.

Produces targeted, minimal questions to resolve underspecification.
Questions are derived deterministically from missing information,
not invented from assumptions.
"""

from __future__ import annotations

from agent_solution.intake.models import ClarifyingQuestion, TaskType


def generate_clarifications(
    task_type: TaskType,
    text: str,
    *,
    missing_paths: bool = False,
    missing_error_info: bool = False,
    missing_validation_criteria: bool = False,
    missing_target_env: bool = False,
    mixed_goals: bool = False,
) -> tuple[ClarifyingQuestion, ...]:
    """Generate targeted clarifying questions for underspecified requests.

    Each question is justified by a concrete reason.  Questions that can
    be answered from deterministic repository context are NOT generated.
    """
    questions: list[ClarifyingQuestion] = []

    if task_type == TaskType.BUG_DIAGNOSIS:
        questions.append(
            ClarifyingQuestion(
                question="What behavior did you observe?",
                reason="Bug diagnosis requires an observed symptom.",
                priority=1,
            )
        )
        questions.append(
            ClarifyingQuestion(
                question="What behavior did you expect?",
                reason="Expected vs. actual comparison is essential for diagnosis.",
                priority=2,
            )
        )
        if missing_error_info:
            questions.append(
                ClarifyingQuestion(
                    question=(
                        "Can you provide an error message, logs, reproduction "
                        "steps, or the relevant change?"
                    ),
                    reason="No error evidence was provided.",
                    priority=3,
                )
            )

    elif task_type == TaskType.READINESS_ASSESSMENT:
        if missing_target_env:
            questions.append(
                ClarifyingQuestion(
                    question="Which target environment is being assessed?",
                    reason=(
                        "Readiness assessment requires a specific deployment target."
                    ),
                    priority=1,
                )
            )
        if missing_validation_criteria:
            questions.append(
                ClarifyingQuestion(
                    question="What acceptance checks are required?",
                    reason="Readiness criteria must be explicit.",
                    priority=2,
                )
            )
        questions.append(
            ClarifyingQuestion(
                question="Which risks are blocking versus advisory?",
                reason="Risk tolerance must be defined for readiness decisions.",
                priority=3,
            )
        )

    elif task_type == TaskType.PATCH_PROPOSAL:
        if missing_paths:
            questions.append(
                ClarifyingQuestion(
                    question="Which files or behavior should change?",
                    reason="Patch proposal requires explicit target area.",
                    priority=1,
                )
            )
        questions.append(
            ClarifyingQuestion(
                question="What must remain unchanged?",
                reason="Scope boundaries prevent unintended side effects.",
                priority=2,
            )
        )
        questions.append(
            ClarifyingQuestion(
                question="How should success be validated?",
                reason="Acceptance criteria must be defined before patching.",
                priority=3,
            )
        )

    elif task_type == TaskType.CODE_REVIEW:
        if missing_paths:
            questions.append(
                ClarifyingQuestion(
                    question="Which files or changes should be reviewed?",
                    reason=(
                        "Review scope is unclear without paths or a diff."
                    ),
                    priority=1,
                )
            )

    elif task_type == TaskType.UNKNOWN:
        questions.append(
            ClarifyingQuestion(
                question="Could you describe what you would like me to do?",
                reason="The request is materially underspecified.",
                priority=1,
            )
        )

    if mixed_goals:
        questions.append(
            ClarifyingQuestion(
                question=(
                    "This request mixes multiple distinct goals (e.g., review, "
                    "patch proposal, readiness assessment). Each requires different "
                    "evidence and execution contracts. Please decompose into a "
                    "single primary task per request."
                ),
                reason=(
                    "Review, patch proposal, and readiness assessment have "
                    "different required evidence and execution contracts. "
                    "Mixed goals prevent focused, evidence-based execution."
                ),
                priority=0,
            )
        )

    return tuple(questions)
