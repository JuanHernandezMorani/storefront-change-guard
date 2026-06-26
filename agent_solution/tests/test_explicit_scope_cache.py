"""Regression tests for explicit-scope Phase 03 caching."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from agent_solution.analysis.evidence import EvidenceBundleBuilder
from agent_solution.analysis.models import AnalysisStatus, ModelExecutionResult
from agent_solution.analysis.orchestrator import AnalysisOrchestrator
from agent_solution.git_tools.collector import collect_git_context
from agent_solution.git_tools.models import ScopeMode
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
    (repo / "unrelated.md").write_text("# Baseline\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "baseline"], cwd=repo, check=True, capture_output=True)

    # Force an unrelated diff to exceed the collector's capture budget.
    (repo / "unrelated.md").write_text("x" * 1_200_000, encoding="utf-8")
    return repo


def _intake():
    return process_request(
        request_id="explicit-cache-regression",
        text="Review shipping.py.",
        has_diff=True,
        has_working_tree=True,
    )


def _valid_output() -> str:
    return json.dumps(
        {
            "analysis_mode": "CODE_REVIEW",
            "summary": "shipping.py contains a threshold-based shipping function.",
            "claims": [
                {
                    "claim_id": "C1",
                    "text": "calculate_shipping returns zero at or above the threshold.",
                    "claim_status": "VERIFIED",
                    "evidence_ids": ["E1"],
                    "inference_basis": None,
                    "limitations": [],
                }
            ],
            "findings": [],
            "next_safe_action": "Review boundary tests before any patch.",
            "phase_limitations": [],
        }
    )


def test_explicit_file_scope_is_cache_complete_despite_unrelated_truncated_diff(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path)
    snapshot = collect_git_context(repository_root=repo, scope_mode=ScopeMode.WORKING_TREE_DIFF)
    assert not snapshot.repository_fingerprint.is_complete_for_cache

    bundle = EvidenceBundleBuilder().build("ar-cache", _intake(), snapshot, repo)

    assert bundle is not None
    assert bundle.repository_fingerprint_complete_for_cache
    assert bundle.repository_fingerprint.startswith("explicit-scope-v1:")
    assert len(bundle.evidence_records) == 1
    assert bundle.evidence_records[0].relative_path == "shipping.py"


def test_explicit_file_scope_hits_cache_despite_unrelated_truncated_diff(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = _init_repo(tmp_path)
    snapshot = collect_git_context(repository_root=repo, scope_mode=ScopeMode.WORKING_TREE_DIFF)
    calls: list[object] = []

    def fake_run_model(config, prompt, max_output_bytes):
        calls.append(config)
        return ModelExecutionResult(
            success=True,
            stdout=_valid_output(),
            stderr="",
            exit_code=0,
            timed_out=False,
            duration_ms=1,
        )

    monkeypatch.setattr("agent_solution.analysis.orchestrator.run_model", fake_run_model)
    orchestrator = AnalysisOrchestrator(state_dir=tmp_path / "state")

    first = orchestrator.analyze(_intake(), snapshot, repo, output_language="en")
    second = orchestrator.analyze(_intake(), snapshot, repo, output_language="en")

    assert first.status is AnalysisStatus.ANALYSIS_COMPLETED
    assert second.status is AnalysisStatus.ANALYSIS_CACHE_HIT
    assert second.cache_hit is True
    assert second.model_id == first.model_id
    assert second.runtime_profile_version == first.runtime_profile_version
    assert second.prompt_schema_version == first.prompt_schema_version
    assert len(calls) == 1
