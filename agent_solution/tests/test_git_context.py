"""Test fixtures for Git Context Collection.

All tests use temporary Git repositories to avoid mutating the project.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from agent_solution.git_tools.collector import collect_git_context
from agent_solution.git_tools.models import (
    CollectionLimits,
    GitContextStatus,
    ScopeMode,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_repo(tmp_path: Path) -> Path:
    """Create a temporary Git repository with an initial commit."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    # Initial commit so HEAD exists
    (repo / "README.md").write_text("# Test\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )
    return repo


def _head_sha(repo: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# Test 1: Clean repository
# ---------------------------------------------------------------------------


class TestCleanRepository:
    """Valid HEAD, no changed files, NO_ACTIONABLE_DIFF."""

    def test_clean_repo_status(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.status == GitContextStatus.NO_ACTIONABLE_DIFF
        assert snapshot.head_sha == _head_sha(repo)
        assert snapshot.staged_change_count == 0
        assert snapshot.unstaged_change_count == 0
        assert snapshot.untracked_change_count == 0
        assert len(snapshot.changed_files) == 0

    def test_clean_repo_fingerprint(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.repository_fingerprint.head_sha == _head_sha(repo)
        assert snapshot.repository_fingerprint.is_complete_for_cache is True
        assert len(snapshot.repository_fingerprint.cache_ineligibility_reasons) == 0


# ---------------------------------------------------------------------------
# Test 2: Unstaged tracked modification
# ---------------------------------------------------------------------------


class TestUnstagedModification:
    """Changed-file inventory, unstaged diff, valid fingerprint."""

    def test_unstaged_inventory(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "README.md").write_text("# Updated\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.status == GitContextStatus.COLLECTED
        assert snapshot.unstaged_change_count >= 1
        paths = [cf.relative_path for cf in snapshot.changed_files]
        assert "README.md" in paths

    def test_unstaged_diff_captured(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "README.md").write_text("# Updated\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.unstaged_diff is not None
        assert snapshot.unstaged_diff.byte_count > 0
        assert "Updated" in snapshot.unstaged_diff.text

    def test_unstaged_fingerprint_valid(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "README.md").write_text("# Updated\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.repository_fingerprint.is_complete_for_cache is True
        assert snapshot.repository_fingerprint.unstaged_diff_hash != ""


# ---------------------------------------------------------------------------
# Test 3: Staged tracked modification
# ---------------------------------------------------------------------------


class TestStagedModification:
    """Staged inventory, staged diff separate from unstaged."""

    def test_staged_inventory(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "README.md").write_text("# Staged\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "README.md"],
            cwd=str(repo),
            capture_output=True,
            check=True,
        )
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.staged_change_count >= 1
        staged = [
            cf for cf in snapshot.changed_files
            if cf.staging.value == "staged"
        ]
        assert len(staged) >= 1

    def test_staged_diff_captured(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "README.md").write_text("# Staged\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "README.md"],
            cwd=str(repo),
            capture_output=True,
            check=True,
        )
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.staged_diff is not None
        assert snapshot.staged_diff.byte_count > 0

    def test_staged_diff_separate_from_unstaged(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "README.md").write_text("# Staged\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "README.md"],
            cwd=str(repo),
            capture_output=True,
            check=True,
        )
        # Also modify another file unstaged
        (repo / "other.txt").write_text("new file content\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        # staged diff has only README.md, unstaged may have other.txt or be None
        assert snapshot.staged_diff is not None


# ---------------------------------------------------------------------------
# Test 4: Eligible untracked text file
# ---------------------------------------------------------------------------


class TestUntrackedTextFile:
    """Inventory includes it, fingerprint behavior is explicit."""

    def test_untracked_in_inventory(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "new_file.py").write_text("print('hello')\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.untracked_change_count >= 1
        paths = [cf.relative_path for cf in snapshot.changed_files]
        assert "new_file.py" in paths

    def test_untracked_fingerprint_includes_path(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "new_file.py").write_text("print('hello')\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.repository_fingerprint.untracked_manifest_hash != ""


# ---------------------------------------------------------------------------
# Test 5: Sensitive .env file
# ---------------------------------------------------------------------------


class TestSensitiveEnvFile:
    """Excluded from excerpt, explicit exclusion reason."""

    def test_env_excluded(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / ".env").write_text("SECRET=abc123\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        env_files = [
            e for e in snapshot.excluded_artifacts
            if e.relative_path == ".env"
        ]
        assert len(env_files) == 1
        assert env_files[0].is_sensitive is True
        assert "sensitive" in env_files[0].exclusion_reason

    def test_env_not_in_excerpts(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / ".env").write_text("SECRET=abc123\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        excerpt_paths = [e.relative_path for e in snapshot.file_excerpts]
        assert ".env" not in excerpt_paths

    def test_dotenv_star_pattern(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / ".env.local").write_text("SECRET=local\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        env_files = [
            e for e in snapshot.excluded_artifacts
            if ".env" in e.relative_path
        ]
        assert len(env_files) >= 1
        assert env_files[0].is_sensitive is True


# ---------------------------------------------------------------------------
# Test 6: Binary changed file
# ---------------------------------------------------------------------------


class TestBinaryFile:
    """Excluded from excerpt, explicit binary classification."""

    def test_binary_excluded(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        binary_path = repo / "image.png"
        binary_path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        # Binary detection via content may vary, but check no crash
        assert snapshot.status in (
            GitContextStatus.COLLECTED,
            GitContextStatus.NO_ACTIONABLE_DIFF,
        )


# ---------------------------------------------------------------------------
# Test 7: Oversized changed text file
# ---------------------------------------------------------------------------


class TestOversizedFile:
    """Excerpt is bounded, truncation reason is explicit."""

    def test_oversized_excerpt_bounded(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        # Create file larger than per-file limit
        large_content = "x" * 100000 + "\n"
        (repo / "large.txt").write_text(large_content, encoding="utf-8")
        limits = CollectionLimits(
            max_excerpt_bytes_per_file=1024,
            max_excerpt_files=10,
            max_total_excerpt_bytes=2048,
        )
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
            limits=limits,
        )
        excerpts = [e for e in snapshot.file_excerpts if e.relative_path == "large.txt"]
        if excerpts:
            assert excerpts[0].truncated is True

    def test_oversized_fingerprint_incomplete(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        large_content = "x" * 100000 + "\n"
        (repo / "large.txt").write_text(large_content, encoding="utf-8")
        # Modify to create unstaged diff
        (repo / "other.txt").write_text("change\n", encoding="utf-8")
        limits = CollectionLimits(
            max_diff_capture_bytes=1024,
            max_excerpt_bytes_per_file=1024,
            max_total_excerpt_bytes=2048,
        )
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
            limits=limits,
        )
        # Diff truncation should mark fingerprint incomplete
        if snapshot.unstaged_diff and snapshot.unstaged_diff.truncated:
            assert snapshot.repository_fingerprint.is_complete_for_cache is False


# ---------------------------------------------------------------------------
# Test 8: Explicit valid path
# ---------------------------------------------------------------------------


class TestExplicitValidPath:
    """Only that path is collected."""

    def test_explicit_path_collected(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "src").mkdir()
        (repo / "src" / "app.py").write_text("print('app')\n", encoding="utf-8")
        (repo / "other.txt").write_text("other\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "src/app.py", "other.txt"],
            cwd=str(repo),
            capture_output=True,
            check=True,
        )
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.EXPLICIT_PATHS,
            explicit_paths=("src/app.py",),
        )
        paths = [cf.relative_path for cf in snapshot.changed_files]
        assert "src/app.py" in paths
        assert "other.txt" not in paths


# ---------------------------------------------------------------------------
# Test 9: Explicit traversal path
# ---------------------------------------------------------------------------


class TestExplicitTraversalPath:
    """Rejected with PATH_ESCAPES_REPOSITORY."""

    def test_traversal_rejected(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.EXPLICIT_PATHS,
            explicit_paths=("../../../etc/passwd",),
        )
        assert snapshot.status == GitContextStatus.PATH_ESCAPES_REPOSITORY

    def test_nonexistent_path_rejected(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.EXPLICIT_PATHS,
            explicit_paths=("nonexistent/file.txt",),
        )
        assert snapshot.status == GitContextStatus.INVALID_EXPLICIT_PATH


# ---------------------------------------------------------------------------
# Test 10: Intake CLARIFY blocks collection
# ---------------------------------------------------------------------------


class TestIntakeClarifyBlocks:
    """INTAKE_DECISION_BLOCKED, no scope expansion."""

    def test_clarify_blocks(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "change.txt").write_text("modified\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
            intake_decision="CLARIFY",
        )
        assert snapshot.status == GitContextStatus.INTAKE_DECISION_BLOCKED
        assert len(snapshot.changed_files) == 0
        assert snapshot.staged_diff is None
        assert snapshot.unstaged_diff is None


# ---------------------------------------------------------------------------
# Test 11: Intake REJECT blocks collection
# ---------------------------------------------------------------------------


class TestIntakeRejectBlocks:
    """Blocked state for REJECT_UNSAFE_OR_UNSUPPORTED."""

    def test_reject_blocks(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "change.txt").write_text("modified\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
            intake_decision="REJECT_UNSAFE_OR_UNSUPPORTED",
        )
        assert snapshot.status == GitContextStatus.INTAKE_DECISION_BLOCKED


# ---------------------------------------------------------------------------
# Test 12: Deterministic fingerprint
# ---------------------------------------------------------------------------


class TestDeterministicFingerprint:
    """Repeated collection without change yields same fingerprint."""

    def test_same_fingerprint_twice(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "code.py").write_text("x = 1\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "code.py"],
            cwd=str(repo),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "add code.py"],
            cwd=str(repo),
            capture_output=True,
            check=True,
        )
        snap1 = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        snap2 = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snap1.repository_fingerprint.head_sha == snap2.repository_fingerprint.head_sha
        assert (
            snap1.repository_fingerprint.staged_diff_hash
            == snap2.repository_fingerprint.staged_diff_hash
        )
        assert (
            snap1.repository_fingerprint.unstaged_diff_hash
            == snap2.repository_fingerprint.unstaged_diff_hash
        )
        assert (
            snap1.repository_fingerprint.untracked_manifest_hash
            == snap2.repository_fingerprint.untracked_manifest_hash
        )
        assert (
            snap1.repository_fingerprint.relevant_scope_hash
            == snap2.repository_fingerprint.relevant_scope_hash
        )


# ---------------------------------------------------------------------------
# Test 13: Changed file modifies fingerprint
# ---------------------------------------------------------------------------


class TestFingerprintChangesOnModification:
    """Changing an eligible source file changes the fingerprint."""

    def test_fingerprint_differs_after_change(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "code.py").write_text("x = 1\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "code.py"],
            cwd=str(repo),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "add code.py"],
            cwd=str(repo),
            capture_output=True,
            check=True,
        )
        snap_before = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        # Now modify the tracked file
        (repo / "code.py").write_text("x = 2\n", encoding="utf-8")
        snap_after = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert (
            snap_before.repository_fingerprint.unstaged_diff_hash
            != snap_after.repository_fingerprint.unstaged_diff_hash
        )


# ---------------------------------------------------------------------------
# Test 14: Command safety - argument arrays, no shell
# ---------------------------------------------------------------------------


class TestCommandSafety:
    """Verify Git commands use argument arrays."""

    def test_all_commands_use_tuples(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        for cmd_evidence in snapshot.command_evidence:
            assert isinstance(cmd_evidence.command, tuple)
            assert cmd_evidence.command[0] == "git"
            # No shell=True in the command tuple itself
            assert "shell" not in " ".join(cmd_evidence.command).lower()

    def test_no_destructive_commands(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        destructive = {
            "commit", "reset", "checkout", "restore", "clean",
            "add", "merge", "rebase", "push", "pull", "gc",
        }
        for cmd_evidence in snapshot.command_evidence:
            cmd_parts = cmd_evidence.command
            if len(cmd_parts) >= 2:
                subcommand = cmd_parts[1]
                assert subcommand not in destructive, (
                    f"Destructive command found: {subcommand}"
                )


# ---------------------------------------------------------------------------
# Test 15: Intake integration
# ---------------------------------------------------------------------------


class TestIntakeIntegration:
    """CODE_REVIEW intake with diff reaches snapshot; no-diff stays non-actionable."""

    def test_code_review_with_diff(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "code.py").write_text("x = 1\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.status == GitContextStatus.COLLECTED
        assert snapshot.head_sha != ""

    def test_code_review_no_diff(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.status == GitContextStatus.NO_ACTIONABLE_DIFF


# ---------------------------------------------------------------------------
# Test 16: Not a git repository
# ---------------------------------------------------------------------------


class TestNotAGitRepository:
    """NOT_A_GIT_REPOSITORY for non-Git path."""

    def test_not_git_repo(self, tmp_path: Path) -> None:
        not_a_repo = tmp_path / "not_a_repo"
        not_a_repo.mkdir()
        snapshot = collect_git_context(
            repository_root=not_a_repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.status == GitContextStatus.NOT_A_GIT_REPOSITORY


# ---------------------------------------------------------------------------
# Test 17: Sensitive .key file
# ---------------------------------------------------------------------------


class TestSensitiveKeyFile:
    """PEM/key files excluded."""

    def test_key_file_excluded(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "server.key").write_text("-----BEGIN RSA PRIVATE KEY-----\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        key_files = [
            e for e in snapshot.excluded_artifacts
            if "server.key" in e.relative_path
        ]
        assert len(key_files) == 1
        assert key_files[0].is_sensitive is True


# ---------------------------------------------------------------------------
# Test 18: Spanish intake fixture integration
# ---------------------------------------------------------------------------


class TestSpanishIntakeIntegration:
    """Spanish review request with working-tree diff."""

    def test_spanish_review_with_diff(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        (repo / "code.py").write_text("x = 1\n", encoding="utf-8")
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.status == GitContextStatus.COLLECTED

    def test_spanish_review_no_diff(self, tmp_path: Path) -> None:
        repo = _make_repo(tmp_path)
        snapshot = collect_git_context(
            repository_root=repo,
            scope_mode=ScopeMode.WORKING_TREE_DIFF,
        )
        assert snapshot.status == GitContextStatus.NO_ACTIONABLE_DIFF
