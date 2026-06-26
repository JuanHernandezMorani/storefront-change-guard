from __future__ import annotations

import subprocess
from pathlib import Path

from agent_solution.analysis.evidence import EvidenceBundleBuilder
from agent_solution.git_tools.collector import collect_git_context
from agent_solution.git_tools.models import ScopeMode
from agent_solution.intake.classifier import extract_file_targets
from agent_solution.intake.models import IntakeDecision, TaskType
from agent_solution.intake.policy import process_request


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    for command in (
        ["git", "init"],
        ["git", "config", "user.email", "test@example.invalid"],
        ["git", "config", "user.name", "Phase 03 Test"],
    ):
        subprocess.run(command, cwd=repo, check=True, capture_output=True)

    (repo / "shipping.py").write_text(
        "FREE_SHIPPING_THRESHOLD_CENTS = 5_000\n\n"
        "def calculate_shipping(subtotal_cents: int) -> int:\n"
        "    if subtotal_cents >= FREE_SHIPPING_THRESHOLD_CENTS:\n"
        "        return 0\n"
        "    return 700\n",
        encoding="utf-8",
    )
    (repo / "unrelated.md").write_text("baseline\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "baseline"], cwd=repo, check=True, capture_output=True)
    (repo / "unrelated.md").write_text("x" * 40_000, encoding="utf-8")
    return repo


def test_ascii_spanish_question_extracts_only_safe_relative_python_targets() -> None:
    assert extract_file_targets("Que hace calculate_shipping en shipping.py?") == ("shipping.py",)
    assert extract_file_targets("Review agent_solution/analysis/evidence.py.") == (
        "agent_solution/analysis/evidence.py",
    )
    assert extract_file_targets("Review ../secrets.py") == ()
    assert extract_file_targets("Review /tmp/secrets.py") == ()


def test_ascii_spanish_question_uses_explicit_file_scope_not_generic_search(tmp_path: Path) -> None:
    intake = process_request(
        request_id="phase03-ascii-spanish-path",
        text="Que hace calculate_shipping en shipping.py?",
        has_diff=True,
        has_working_tree=True,
    )

    assert intake.detected_task_type is TaskType.CODEBASE_QUESTION
    assert intake.decision is IntakeDecision.ACCEPT_WITH_SAFE_DEFAULTS
    assert intake.safe_defaults.scope_source == "explicit_file_paths"
    assert intake.resolved_scope.explicit_file_targets == ("shipping.py",)

    repo = _init_repo(tmp_path)
    snapshot = collect_git_context(repository_root=repo, scope_mode=ScopeMode.WORKING_TREE_DIFF)
    bundle = EvidenceBundleBuilder().build("ar-ascii-spanish", intake, snapshot, repo)

    assert bundle is not None
    assert len(bundle.evidence_records) == 1
    assert bundle.evidence_records[0].relative_path == "shipping.py"
    assert "calculate_shipping" in bundle.evidence_records[0].content
    assert all("unrelated.md" not in record.content for record in bundle.evidence_records)
