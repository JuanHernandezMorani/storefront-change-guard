"""Deterministic Git context collector.

Read-only evidence collection from a Git repository.  Produces a
GitContextSnapshot that later phases can safely consume without
model calls or repository mutation.
"""

from __future__ import annotations

import hashlib
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from agent_solution.git_tools.excerpts import collect_excerpts
from agent_solution.git_tools.fingerprint import build_fingerprint
from agent_solution.git_tools.models import (
    ChangedFile,
    ChangeKind,
    CollectionLimits,
    DiffArtifact,
    ExcludedArtifact,
    GitCommandEvidence,
    GitContextSnapshot,
    GitContextStatus,
    ScopeMode,
    StagingStatus,
)

# Sensitive basename and extension patterns (conservative).
_SENSITIVE_BASENAMES: frozenset[str] = frozenset({
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
})

_SENSITIVE_PREFIXES: tuple[str, ...] = (
    ".env",
    "credentials",
    "secrets",
    "token",
)

_SENSITIVE_EXTENSIONS: frozenset[str] = frozenset({
    ".pem",
    ".key",
    ".pfx",
    ".p12",
})


def _is_sensitive_path(path_str: str) -> bool:
    """Conservative sensitive-file detection by basename and extension."""
    name = Path(path_str).name.lower()
    if name in _SENSITIVE_BASENAMES:
        return True
    for prefix in _SENSITIVE_PREFIXES:
        if name.startswith(prefix):
            return True
    suffix = Path(path_str).suffix.lower()
    if suffix in _SENSITIVE_EXTENSIONS:
        return True
    return False


@dataclass(frozen=True, slots=True)
class _GitResult:
    """Internal result pairing evidence record with output content."""

    evidence: GitCommandEvidence
    stdout: str
    stderr: str


def _run_git(
    args: list[str],
    cwd: Path,
    timeout: int = 20,
    max_output: int = 1048576,
) -> _GitResult:
    """Execute a Git command safely with argument arrays.

    Never uses shell=True.  Captures stdout/stderr with bounds.
    Returns evidence record paired with actual output content.
    """
    cmd = ["git"] + args
    start = time.monotonic()
    timed_out = False
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        exit_code = result.returncode
        stdout = result.stdout[:max_output]
        stderr = result.stderr[:max_output]
    except subprocess.TimeoutExpired:
        timed_out = True
        exit_code = -1
        stdout = ""
        stderr = "Command timed out"
    except FileNotFoundError:
        return _GitResult(
            evidence=GitCommandEvidence(
                command=tuple(cmd),
                exit_code=-1,
                stdout_length=0,
                stderr_length=0,
                timed_out=False,
                cwd=str(cwd),
                duration_ms=0,
            ),
            stdout="",
            stderr="git not found",
        )
    except Exception as exc:  # noqa: BLE001
        return _GitResult(
            evidence=GitCommandEvidence(
                command=tuple(cmd),
                exit_code=-1,
                stdout_length=0,
                stderr_length=len(str(exc)),
                timed_out=False,
                cwd=str(cwd),
                duration_ms=0,
            ),
            stdout="",
            stderr=str(exc),
        )

    duration_ms = int((time.monotonic() - start) * 1000)
    return _GitResult(
        evidence=GitCommandEvidence(
            command=tuple(cmd),
            exit_code=exit_code,
            stdout_length=len(stdout),
            stderr_length=len(stderr),
            timed_out=timed_out,
            cwd=str(cwd),
            duration_ms=duration_ms,
        ),
        stdout=stdout,
        stderr=stderr,
    )


def _capture_diff(
    args: list[str],
    cwd: Path,
    limits: CollectionLimits,
) -> DiffArtifact:
    """Capture a diff artifact with truncation tracking."""
    cmd = ["git"] + args
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=limits.command_timeout_seconds,
            shell=False,
        )
        raw_text = result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        raw_text = ""

    byte_count = len(raw_text.encode("utf-8"))
    truncated = byte_count > limits.max_diff_capture_bytes
    if truncated:
        raw_text = raw_text.encode("utf-8")[:limits.max_diff_capture_bytes].decode(
            "utf-8", errors="replace"
        )
        byte_count = len(raw_text.encode("utf-8"))

    sha256 = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

    file_count = 0
    for line in raw_text.split("\n"):
        if line.startswith("diff --git"):
            file_count += 1

    return DiffArtifact(
        diff_type=" ".join(args[:2]) if len(args) >= 2 else "diff",
        text=raw_text,
        sha256=sha256,
        byte_count=byte_count,
        truncated=truncated,
        captured_limit=limits.max_diff_capture_bytes,
        file_count=file_count,
    )


def _parse_status_porcelain(
    status_text: str,
) -> tuple[int, int, int]:
    """Parse git status --porcelain=v1 -z output.

    Returns (staged_count, unstaged_count, untracked_count).
    """
    if not status_text.strip():
        return 0, 0, 0

    staged = 0
    unstaged = 0
    untracked = 0

    parts = status_text.split("\0")
    i = 0
    while i < len(parts):
        part = parts[i]
        if len(part) < 2:
            i += 1
            continue
        xy = part[:2]
        if xy[0] in ("R", "C") or xy[1] in ("R", "C"):
            i += 3
        else:
            i += 2

        index_status = xy[0]
        worktree_status = xy[1]

        if index_status == "?":
            untracked += 1
        else:
            if index_status != " " and index_status != "?":
                staged += 1
            if worktree_status != " " and worktree_status != "?":
                unstaged += 1

    return staged, unstaged, untracked


def _parse_name_status(
    name_status_text: str,
) -> tuple[ChangedFile, ...]:
    """Parse git diff --name-status output into ChangedFile tuples."""
    files: list[ChangedFile] = []
    if not name_status_text.strip():
        return ()

    for line in name_status_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue

        status_code = parts[0][0] if parts[0] else "X"
        rel_path = parts[-1]

        try:
            kind = ChangeKind(status_code)
        except ValueError:
            kind = ChangeKind.UNKNOWN

        files.append(
            ChangedFile(
                relative_path=rel_path,
                change_kind=kind,
                staging=StagingStatus.STAGED,
                exists_on_disk=True,
                is_regular_file=True,
                is_binary=False,
                is_sensitive=_is_sensitive_path(rel_path),
                size_bytes=0,
                extension=Path(rel_path).suffix,
                eligible_for_excerpt=True,
                exclusion_reason="",
            )
        )
    return tuple(files)


def _build_empty_snapshot(
    *,
    repository_root: str,
    status: GitContextStatus,
    limits: CollectionLimits,
    warnings: tuple[str, ...] = (),
    evidence: tuple[GitCommandEvidence, ...] = (),
    head_sha: str = "",
    branch_name: str = "",
) -> GitContextSnapshot:
    """Build a minimal snapshot for blocked or empty states."""
    from agent_solution.git_tools.models import RepositoryFingerprint

    return GitContextSnapshot(
        status=status,
        repository_root=repository_root,
        repository_relative_root="",
        head_sha=head_sha,
        branch_name_or_detached_state=branch_name,
        status_porcelain="",
        staged_change_count=0,
        unstaged_change_count=0,
        untracked_change_count=0,
        changed_files=(),
        staged_diff=None,
        unstaged_diff=None,
        file_excerpts=(),
        excluded_artifacts=(),
        repository_fingerprint=RepositoryFingerprint(
            head_sha=head_sha,
            staged_diff_hash="",
            unstaged_diff_hash="",
            untracked_manifest_hash="",
            relevant_scope_hash="",
        ),
        collection_limits=limits,
        collection_warnings=warnings,
        command_evidence=evidence,
    )


def collect_git_context(
    *,
    repository_root: Path,
    scope_mode: ScopeMode,
    explicit_paths: tuple[str, ...] = (),
    intake_decision: str = "",
    limits: CollectionLimits | None = None,
) -> GitContextSnapshot:
    """Collect deterministic Git context from a repository.

    Read-only.  No model calls.  No repository mutation.
    """
    if limits is None:
        limits = CollectionLimits()

    root = repository_root.resolve()
    warnings: list[str] = []
    evidence: list[GitCommandEvidence] = []

    # --- Blocked intake decisions ---
    if intake_decision in ("CLARIFY", "REJECT_UNSAFE_OR_UNSUPPORTED"):
        return _build_empty_snapshot(
            repository_root=str(root),
            status=GitContextStatus.INTAKE_DECISION_BLOCKED,
            limits=limits,
            warnings=(f"Intake decision '{intake_decision}' blocks collection.",),
            evidence=evidence,
        )

    # --- Validate Git repository ---
    rev_parse = _run_git(
        ["rev-parse", "--show-toplevel"],
        cwd=root,
        timeout=limits.command_timeout_seconds,
    )
    evidence.append(rev_parse.evidence)

    if rev_parse.evidence.exit_code != 0:
        if "not a git repository" in rev_parse.stderr.lower():
            return _build_empty_snapshot(
                repository_root=str(root),
                status=GitContextStatus.NOT_A_GIT_REPOSITORY,
                limits=limits,
                warnings=("Path is not a Git repository.",),
                evidence=evidence,
            )
        return _build_empty_snapshot(
            repository_root=str(root),
            status=GitContextStatus.GIT_COMMAND_FAILED,
            limits=limits,
            warnings=(f"git rev-parse failed: exit_code={rev_parse.evidence.exit_code}",),
            evidence=evidence,
        )

    repo_root_str = rev_parse.stdout.strip()
    rel_root = str(root.relative_to(Path(repo_root_str))) if repo_root_str != str(root) else ""

    # --- HEAD SHA ---
    head_cmd = _run_git(["rev-parse", "HEAD"], cwd=root, timeout=limits.command_timeout_seconds)
    evidence.append(head_cmd.evidence)
    head_sha = head_cmd.stdout.strip() if head_cmd.evidence.exit_code == 0 else ""

    # --- Branch name ---
    branch_cmd = _run_git(
        ["branch", "--show-current"], cwd=root, timeout=limits.command_timeout_seconds
    )
    evidence.append(branch_cmd.evidence)
    branch_name = branch_cmd.stdout.strip() if branch_cmd.evidence.exit_code == 0 else ""
    if not branch_name and head_sha:
        branch_name = "HEAD detached"

    # --- Status porcelain ---
    status_cmd = _run_git(
        ["status", "--porcelain=v1", "-z"],
        cwd=root,
        timeout=limits.command_timeout_seconds,
    )
    evidence.append(status_cmd.evidence)
    status_porcelain = status_cmd.stdout if status_cmd.evidence.exit_code == 0 else ""

    staged_count, unstaged_count, untracked_count = _parse_status_porcelain(status_porcelain)

    # --- Name-status for staged and unstaged ---
    staged_ns = _run_git(
        ["diff", "--cached", "--name-status", "--no-ext-diff", "--no-color"],
        cwd=root,
        timeout=limits.command_timeout_seconds,
    )
    evidence.append(staged_ns.evidence)
    staged_files_raw = (
        _parse_name_status(staged_ns.stdout) if staged_ns.evidence.exit_code == 0 else ()
    )

    unstaged_ns = _run_git(
        ["diff", "--name-status", "--no-ext-diff", "--no-color"],
        cwd=root,
        timeout=limits.command_timeout_seconds,
    )
    evidence.append(unstaged_ns.evidence)
    unstaged_files_raw = (
        _parse_name_status(unstaged_ns.stdout) if unstaged_ns.evidence.exit_code == 0 else ()
    )

    # Mark staging status by creating new instances (frozen dataclasses)
    staged_files = tuple(
        ChangedFile(
            relative_path=cf.relative_path,
            change_kind=cf.change_kind,
            staging=StagingStatus.STAGED,
            exists_on_disk=cf.exists_on_disk,
            is_regular_file=cf.is_regular_file,
            is_binary=cf.is_binary,
            is_sensitive=cf.is_sensitive,
            size_bytes=cf.size_bytes,
            extension=cf.extension,
            eligible_for_excerpt=cf.eligible_for_excerpt,
            exclusion_reason=cf.exclusion_reason,
        )
        for cf in staged_files_raw
    )
    unstaged_files = tuple(
        ChangedFile(
            relative_path=cf.relative_path,
            change_kind=cf.change_kind,
            staging=StagingStatus.UNSTAGED,
            exists_on_disk=cf.exists_on_disk,
            is_regular_file=cf.is_regular_file,
            is_binary=cf.is_binary,
            is_sensitive=cf.is_sensitive,
            size_bytes=cf.size_bytes,
            extension=cf.extension,
            eligible_for_excerpt=cf.eligible_for_excerpt,
            exclusion_reason=cf.exclusion_reason,
        )
        for cf in unstaged_files_raw
    )

    # --- Untracked files ---
    untracked_cmd = _run_git(
        ["ls-files", "--others", "--exclude-standard"],
        cwd=root,
        timeout=limits.command_timeout_seconds,
    )
    evidence.append(untracked_cmd.evidence)
    untracked_paths = (
        tuple(p for p in untracked_cmd.stdout.strip().split("\n") if p.strip())
        if untracked_cmd.evidence.exit_code == 0
        else ()
    )

    untracked_files = tuple(
        ChangedFile(
            relative_path=p,
            change_kind=ChangeKind.ADDED,
            staging=StagingStatus.UNTRACKED,
            exists_on_disk=(root / p).exists(),
            is_regular_file=(root / p).is_file() if (root / p).exists() else False,
            is_binary=False,
            is_sensitive=_is_sensitive_path(p),
            size_bytes=(root / p).stat().st_size if (root / p).exists() else 0,
            extension=Path(p).suffix,
            eligible_for_excerpt=True,
            exclusion_reason="",
        )
        for p in untracked_paths
    )

    # --- Combine all changed files ---
    all_changed = staged_files + unstaged_files + untracked_files

    # Apply file limit
    if len(all_changed) > limits.max_changed_files:
        warnings.append(
            f"Changed file count ({len(all_changed)}) exceeds limit "
            f"({limits.max_changed_files}). Truncating."
        )
        all_changed = all_changed[: limits.max_changed_files]

    # --- Capture diffs (before early returns) ---
    staged_diff: DiffArtifact | None = None
    if staged_files:
        staged_diff = _capture_diff(
            ["diff", "--cached", "--no-ext-diff", "--no-color", "--unified=3"],
            cwd=root,
            limits=limits,
        )

    unstaged_diff: DiffArtifact | None = None
    if unstaged_files:
        unstaged_diff = _capture_diff(
            ["diff", "--no-ext-diff", "--no-color", "--unified=3"],
            cwd=root,
            limits=limits,
        )

    # --- Handle scope modes ---
    if scope_mode == ScopeMode.NO_ACTIONABLE_SCOPE:
        return _build_empty_snapshot(
            repository_root=str(root),
            status=GitContextStatus.NO_ACTIONABLE_DIFF,
            limits=limits,
            warnings=warnings,
            evidence=evidence,
            head_sha=head_sha,
            branch_name=branch_name,
        )

    if scope_mode == ScopeMode.WORKING_TREE_DIFF:
        if not all_changed:
            return _build_empty_snapshot(
                repository_root=str(root),
                status=GitContextStatus.NO_ACTIONABLE_DIFF,
                limits=limits,
                warnings=warnings,
                evidence=evidence,
                head_sha=head_sha,
                branch_name=branch_name,
            )

    if scope_mode == ScopeMode.EXPLICIT_PATHS:
        valid_paths: list[str] = []
        for p in explicit_paths:
            normalized = (root / p).resolve()
            if not str(normalized).startswith(str(root)):
                return _build_empty_snapshot(
                    repository_root=str(root),
                    status=GitContextStatus.PATH_ESCAPES_REPOSITORY,
                    limits=limits,
                    warnings=(f"Path escapes repository root: {p}",),
                    evidence=evidence,
                )
            if not normalized.exists():
                return _build_empty_snapshot(
                    repository_root=str(root),
                    status=GitContextStatus.INVALID_EXPLICIT_PATH,
                    limits=limits,
                    warnings=(f"Path does not exist: {p}",),
                    evidence=evidence,
                )
            if ".git" in normalized.parts:
                return _build_empty_snapshot(
                    repository_root=str(root),
                    status=GitContextStatus.INVALID_EXPLICIT_PATH,
                    limits=limits,
                    warnings=(f"Path targets .git directory: {p}",),
                    evidence=evidence,
                )
            valid_paths.append(p)

        valid_set = set(valid_paths)
        all_changed = tuple(cf for cf in all_changed if cf.relative_path in valid_set)

    if scope_mode == ScopeMode.BOUNDED_REPOSITORY_SEARCH:
        pass

    # --- Collect excerpts ---
    excerpts, excluded = collect_excerpts(all_changed, root, limits)

    # --- Mark sensitive/binary exclusions from changed files ---
    for cf in all_changed:
        if cf.is_binary and not any(e.relative_path == cf.relative_path for e in excluded):
            excluded = excluded + (
                ExcludedArtifact(
                    relative_path=cf.relative_path,
                    exclusion_reason="binary_artifact",
                    size_bytes=cf.size_bytes,
                    is_binary=True,
                    is_sensitive=False,
                ),
            )
        if cf.is_sensitive and not any(e.relative_path == cf.relative_path for e in excluded):
            excluded = excluded + (
                ExcludedArtifact(
                    relative_path=cf.relative_path,
                    exclusion_reason="sensitive_artifact",
                    size_bytes=cf.size_bytes,
                    is_binary=False,
                    is_sensitive=True,
                ),
            )

    # --- Build fingerprint ---
    truncated_staged = staged_diff.truncated if staged_diff else False
    truncated_unstaged = unstaged_diff.truncated if unstaged_diff else False
    incomplete_scope = truncated_staged or truncated_unstaged

    fingerprint = build_fingerprint(
        head_sha=head_sha,
        staged_diff=staged_diff,
        unstaged_diff=unstaged_diff,
        untracked_paths=untracked_paths,
        changed_file_paths=tuple(cf.relative_path for cf in all_changed),
        truncated_staged=truncated_staged,
        truncated_unstaged=truncated_unstaged,
        incomplete_scope=incomplete_scope,
        excluded_reasons=tuple(e.exclusion_reason for e in excluded if e.exclusion_reason),
        limits=limits,
    )

    if not fingerprint.is_complete_for_cache:
        warnings.append(
            f"Fingerprint incomplete for cache: "
            f"{', '.join(fingerprint.cache_ineligibility_reasons)}"
        )

    return GitContextSnapshot(
        status=GitContextStatus.COLLECTED,
        repository_root=str(root),
        repository_relative_root=rel_root,
        head_sha=head_sha,
        branch_name_or_detached_state=branch_name,
        status_porcelain=status_porcelain,
        staged_change_count=staged_count,
        unstaged_change_count=unstaged_count,
        untracked_change_count=untracked_count,
        changed_files=all_changed,
        staged_diff=staged_diff,
        unstaged_diff=unstaged_diff,
        file_excerpts=excerpts,
        excluded_artifacts=excluded,
        repository_fingerprint=fingerprint,
        collection_limits=limits,
        collection_warnings=tuple(warnings),
        command_evidence=tuple(evidence),
    )
