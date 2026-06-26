"""Regression tests for explicit-file scope priority in Phase 03."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from agent_solution.analysis.evidence import EvidenceBundleBuilder
from agent_solution.analysis.models import (
    AnalysisStatus,
    ModelExecutionResult,
    SourceKind,
)
from agent_solution.analysis.orchestrator import (
    AnalysisOrchestrator,
    _remove_lowest_priority_evidence,
)
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
    subprocess.run(
        ["git", "commit", "-m", "baseline"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # This intentionally creates a broad, unrelated diff large enough to
    # exceed the small local context budget if generic diff evidence is used.
    (repo / "unrelated.md").write_text("x" * 40_000, encoding="utf-8")
    return repo


def _explicit_shipping_intake():
    return process_request(
        request_id="explicit-scope-regression",
        text="Review shipping.py.",
        has_diff=True,
        has_working_tree=True,
    )


def _valid_review_json() -> str:
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


def test_explicit_target_excludes_unrelated_working_tree_diff(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    intake = _explicit_shipping_intake()
    snapshot = collect_git_context(
        repository_root=repo,
        scope_mode=ScopeMode.WORKING_TREE_DIFF,
    )

    bundle = EvidenceBundleBuilder().build(
        "ar-explicit-scope",
        intake,
        snapshot,
        repo,
    )

    assert bundle is not None
    assert len(bundle.evidence_records) == 1
    assert bundle.evidence_records[0].source_kind is SourceKind.EXPLICIT_PATH
    assert bundle.evidence_records[0].relative_path == "shipping.py"
    assert "calculate_shipping" in bundle.evidence_records[0].content
    assert all(
        record.source_kind is not SourceKind.DIFF_ARTIFACT
        for record in bundle.evidence_records
    )
    assert any(
        "explicit file targets define the Phase 03 scope" in limitation
        for limitation in bundle.collection_limitations
    )


def test_context_reduction_drops_generic_diff_before_explicit_path(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    intake = _explicit_shipping_intake()
    snapshot = collect_git_context(
        repository_root=repo,
        scope_mode=ScopeMode.WORKING_TREE_DIFF,
    )
    bundle = EvidenceBundleBuilder().build(
        "ar-explicit-scope",
        intake,
        snapshot,
        repo,
    )

    assert bundle is not None
    explicit = bundle.evidence_records[0]
    generic_diff = explicit.__class__(
        evidence_id="E2",
        source_kind=SourceKind.DIFF_ARTIFACT,
        relative_path="(unstaged diff)",
        start_line=1,
        end_line=1,
        content="x" * 1_000,
        content_sha256="test",
        byte_count=1_000,
        selection_reason="test",
        provenance="git diff",
    )

    records = [explicit, generic_diff]
    removed = _remove_lowest_priority_evidence(records)

    assert removed.source_kind is SourceKind.DIFF_ARTIFACT
    assert records == [explicit]


def test_explicit_target_still_reaches_model_with_large_unrelated_diff(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = _init_repo(tmp_path)
    intake = _explicit_shipping_intake()
    snapshot = collect_git_context(
        repository_root=repo,
        scope_mode=ScopeMode.WORKING_TREE_DIFF,
    )

    calls = []

    def fake_run_model(config, prompt, max_output_bytes):
        calls.append((config, prompt, max_output_bytes))
        return ModelExecutionResult(
            success=True,
            stdout=_valid_review_json(),
            stderr="",
            exit_code=0,
            timed_out=False,
            duration_ms=1,
        )

    monkeypatch.setattr(
        "agent_solution.analysis.orchestrator.run_model",
        fake_run_model,
    )

    result = AnalysisOrchestrator(
        state_dir=tmp_path / "state",
        no_cache=True,
    ).analyze(
        intake=intake,
        git_snapshot=snapshot,
        repository_root=repo,
        output_language="en",
    )

    assert result.status is AnalysisStatus.ANALYSIS_COMPLETED
    assert len(calls) == 1
    assert "calculate_shipping" in calls[0][1]
    assert "x" * 100 not in calls[0][1]
