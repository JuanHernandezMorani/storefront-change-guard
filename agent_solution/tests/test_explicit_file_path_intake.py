from __future__ import annotations

from agent_solution.intake.models import IntakeDecision, TaskType
from agent_solution.intake.policy import process_request


def test_explicit_python_file_target_supplies_scope_without_caller_flag() -> None:
    result = process_request(
        request_id="explicit-path-cli-regression",
        text="Review shipping.py.",
        has_diff=False,
        has_working_tree=False,
        has_paths=False,
    )

    assert result.detected_task_type is TaskType.CODE_REVIEW
    assert result.decision is IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
    assert result.resolved_scope.explicit_file_targets == ("shipping.py",)
