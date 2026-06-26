"""Phase 04 isolated patch-validation tests."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from agent_solution.patch_validation.models import (
    PatchValidationStatus,
    ValidationProfile,
)
from agent_solution.patch_validation.service import (
    inspect_unified_patch,
    validate_patch,
    write_validation_artifact,
)


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(["init"], repo)
    _git(["config", "user.email", "tests@example.invalid"], repo)
    _git(["config", "user.name", "Storefront Guard Tests"], repo)
    (repo / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(["add", "app.py"], repo)
    _git(["commit", "-m", "baseline"], repo)
    return repo


def _value_patch(before: int, after: int) -> str:
    return (
        "diff --git a/app.py b/app.py\n"
        "index 1111111..2222222 100644\n"
        "--- a/app.py\n"
        "+++ b/app.py\n"
        "@@ -1 +1 @@\n"
        f"-VALUE = {before}\n"
        f"+VALUE = {after}\n"
    )


class TestPatchSafety:
    """Static unified-diff checks occur before any worktree mutation."""

    def test_standard_patch_is_accepted(self) -> None:
        report = inspect_unified_patch(_value_patch(1, 2))
        assert report.accepted is True
        assert report.changed_paths == ("app.py",)
        assert report.rejection_reasons == ()

    def test_traversal_path_is_rejected(self) -> None:
        patch = _value_patch(1, 2).replace("a/app.py b/app.py", "a/../secret b/../secret")
        report = inspect_unified_patch(patch)
        assert report.accepted is False
        assert any(reason.startswith("PATCH_PATH_FORBIDDEN") for reason in report.rejection_reasons)

    def test_sensitive_path_is_rejected(self) -> None:
        patch = _value_patch(1, 2).replace("app.py", ".env", 4)
        report = inspect_unified_patch(patch)
        assert report.accepted is False
        assert any(reason.startswith("PATCH_PATH_FORBIDDEN") for reason in report.rejection_reasons)

    def test_non_allowlisted_path_is_rejected(self) -> None:
        report = inspect_unified_patch(_value_patch(1, 2), allowed_paths=("shipping.py",))
        assert report.accepted is False
        assert report.rejection_reasons == ("PATCH_PATH_NOT_ALLOWLISTED:app.py",)


class TestIsolatedPatchValidation:
    """Patches apply only in detached worktrees and run fixed commands."""

    def test_valid_patch_is_applied_and_validated_without_source_mutation(
        self, tmp_path: Path
    ) -> None:
        repo = _make_repo(tmp_path)
        result = validate_patch(
            repo,
            _value_patch(1, 2),
            validation_profile=ValidationProfile.GIT_DIFF_CHECK,
        )

        assert result.status is PatchValidationStatus.VALIDATED
        assert result.worktree_retained is False
        assert [item.name for item in result.command_results] == [
            "worktree_create",
            "patch_apply_check",
            "patch_apply",
            "git_diff_check",
            "worktree_cleanup",
        ]
        assert all(item.passed for item in result.command_results)
        assert (repo / "app.py").read_text(encoding="utf-8") == "VALUE = 1\n"
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True, check=True
        )
        assert status.stdout == ""

    def test_retain_worktree_records_debug_location(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        result = validate_patch(
            repo,
            _value_patch(1, 2),
            validation_profile=ValidationProfile.GIT_DIFF_CHECK,
            retain_worktree=True,
        )

        assert result.status is PatchValidationStatus.VALIDATED
        assert result.worktree_retained is True
        retained = Path(result.retained_worktree_path)
        assert retained.is_dir()
        assert (retained / "app.py").read_text(encoding="utf-8") == "VALUE = 2\n"
        _git(["worktree", "remove", "--force", str(retained)], repo)
        shutil.rmtree(retained.parent)

    def test_non_applying_patch_never_changes_source_repository(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        result = validate_patch(
            repo,
            _value_patch(999, 2),
            validation_profile=ValidationProfile.GIT_DIFF_CHECK,
        )

        assert result.status is PatchValidationStatus.PATCH_APPLY_FAILED
        assert (repo / "app.py").read_text(encoding="utf-8") == "VALUE = 1\n"
        assert any(
            item.name == "patch_apply_check" and not item.passed for item in result.command_results
        )

    def test_invalid_base_ref_is_rejected_without_worktree(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        result = validate_patch(
            repo,
            _value_patch(1, 2),
            base_ref="not-a-real-ref",
            validation_profile=ValidationProfile.GIT_DIFF_CHECK,
        )

        assert result.status is PatchValidationStatus.INVALID_REQUEST
        assert result.command_results == ()

    def test_machine_readable_artifact_excludes_raw_patch(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        patch = _value_patch(1, 2)
        result = validate_patch(repo, patch, validation_profile=ValidationProfile.GIT_DIFF_CHECK)
        artifact = write_validation_artifact(result, tmp_path / "artifacts")
        raw = artifact.read_text(encoding="utf-8")
        payload = json.loads(raw)

        assert artifact.exists()
        assert payload["status"] == "VALIDATED"
        assert patch not in raw
        assert payload["patch_safety"]["patch_sha256"]
        assert "worktree" not in payload["repository_root"].lower()
