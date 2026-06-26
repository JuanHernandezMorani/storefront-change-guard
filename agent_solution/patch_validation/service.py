"""Deterministic Phase 04 patch application and validation in an isolated worktree.

The source checkout is never modified.  A supplied unified diff is statically
screened, applied only to a detached temporary worktree, and checked through a
small named command allowlist.  No model invocation occurs in this module.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path, PurePosixPath

from agent_solution.patch_validation.models import (
    PatchSafetyReport,
    PatchValidationResult,
    PatchValidationStatus,
    ValidationCommandResult,
    ValidationProfile,
)

_MAX_PATCH_BYTES = 262_144
_MAX_COMMAND_OUTPUT_BYTES = 16_384
_COMMAND_TIMEOUT_SECONDS = 180
_SENSITIVE_BASENAMES = {"id_rsa", "id_ed25519", "id_ecdsa"}
_SENSITIVE_PREFIXES = (".env", "credentials", "secrets", "token")
_SENSITIVE_SUFFIXES = {".pem", ".key", ".pfx", ".p12"}
_DIFF_HEADER = re.compile(r"^diff --git a/(.+) b/(.+)$")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_safe_relative_path(value: str) -> bool:
    path = PurePosixPath(value)
    if not value or value.startswith("/") or "\\" in value:
        return False
    if any(part in {"", ".", "..", ".git"} for part in path.parts):
        return False
    name = path.name.lower()
    if name in _SENSITIVE_BASENAMES:
        return False
    if name.startswith(_SENSITIVE_PREFIXES):
        return False
    if path.suffix.lower() in _SENSITIVE_SUFFIXES:
        return False
    return True


def inspect_unified_patch(
    patch_text: str,
    allowed_paths: tuple[str, ...] = (),
) -> PatchSafetyReport:
    """Validate the diff syntax and all changed paths before any Git command."""
    patch_bytes = len(patch_text.encode("utf-8"))
    reasons: list[str] = []
    changed_paths: list[str] = []

    if not patch_text.strip():
        reasons.append("PATCH_EMPTY")
    if patch_bytes > _MAX_PATCH_BYTES:
        reasons.append("PATCH_EXCEEDS_BYTE_LIMIT")
    if "GIT binary patch" in patch_text or "Binary files " in patch_text:
        reasons.append("PATCH_BINARY_CONTENT_FORBIDDEN")

    for line in patch_text.splitlines():
        match = _DIFF_HEADER.match(line)
        if match is None:
            continue
        left, right = match.groups()
        if left != right:
            reasons.append("PATCH_RENAME_OR_COPY_FORBIDDEN")
            continue
        changed_paths.append(left)

    if not changed_paths:
        reasons.append("PATCH_HAS_NO_STANDARD_DIFF_HEADERS")

    normalized_allowed = tuple(PurePosixPath(path).as_posix() for path in allowed_paths)
    for path in changed_paths:
        if not _is_safe_relative_path(path):
            reasons.append(f"PATCH_PATH_FORBIDDEN:{path}")
            continue
        if normalized_allowed and path not in normalized_allowed:
            reasons.append(f"PATCH_PATH_NOT_ALLOWLISTED:{path}")

    return PatchSafetyReport(
        accepted=not reasons,
        patch_sha256=_sha256_text(patch_text),
        patch_byte_count=patch_bytes,
        changed_paths=tuple(sorted(set(changed_paths))),
        rejection_reasons=tuple(sorted(set(reasons))),
    )


def _run(
    command: tuple[str, ...],
    cwd: Path,
    timeout_seconds: int = _COMMAND_TIMEOUT_SECONDS,
) -> ValidationCommandResult:
    """Run one fixed command without shell interpolation and with bounded output."""
    start = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout_seconds,
            shell=False,
            check=False,
        )
        return ValidationCommandResult(
            name="",
            command=command,
            exit_code=completed.returncode,
            timed_out=False,
            duration_ms=int((time.monotonic() - start) * 1000),
            stdout_excerpt=completed.stdout[:_MAX_COMMAND_OUTPUT_BYTES],
            stderr_excerpt=completed.stderr[:_MAX_COMMAND_OUTPUT_BYTES],
        )
    except FileNotFoundError as exc:
        return ValidationCommandResult(
            name="",
            command=command,
            exit_code=-1,
            timed_out=False,
            duration_ms=int((time.monotonic() - start) * 1000),
            stdout_excerpt="",
            stderr_excerpt=str(exc)[:_MAX_COMMAND_OUTPUT_BYTES],
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return ValidationCommandResult(
            name="",
            command=command,
            exit_code=-1,
            timed_out=True,
            duration_ms=int((time.monotonic() - start) * 1000),
            stdout_excerpt=stdout[:_MAX_COMMAND_OUTPUT_BYTES],
            stderr_excerpt=stderr[:_MAX_COMMAND_OUTPUT_BYTES],
        )


def _named(result: ValidationCommandResult, name: str) -> ValidationCommandResult:
    return ValidationCommandResult(
        name=name,
        command=result.command,
        exit_code=result.exit_code,
        timed_out=result.timed_out,
        duration_ms=result.duration_ms,
        stdout_excerpt=result.stdout_excerpt,
        stderr_excerpt=result.stderr_excerpt,
    )


def _validation_commands(profile: ValidationProfile) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return the closed command allowlist for a named validation profile."""
    git_diff = ("git_diff_check", ("git", "diff", "--check"))
    if profile is ValidationProfile.GIT_DIFF_CHECK:
        return (git_diff,)
    return (
        ("compileall", (sys.executable, "-m", "compileall", "-q", "agent_solution")),
        ("pytest", (sys.executable, "-m", "pytest", "-q")),
        ("ruff", (sys.executable, "-m", "ruff", "check", "agent_solution", "scripts")),
        git_diff,
    )


def _git_available(repository_root: Path) -> bool:
    result = _run(("git", "rev-parse", "--is-inside-work-tree"), repository_root, 20)
    return result.passed and result.stdout_excerpt.strip() == "true"


def _safe_base_ref(repository_root: Path, base_ref: str) -> bool:
    if not base_ref or base_ref.startswith("-"):
        return False
    result = _run(("git", "rev-parse", "--verify", f"{base_ref}^{{commit}}"), repository_root, 20)
    return result.passed


def _empty_safety(patch_text: str, reason: str) -> PatchSafetyReport:
    return PatchSafetyReport(
        accepted=False,
        patch_sha256=_sha256_text(patch_text),
        patch_byte_count=len(patch_text.encode("utf-8")),
        changed_paths=(),
        rejection_reasons=(reason,),
    )


def validate_patch(
    repository_root: Path,
    patch_text: str,
    *,
    base_ref: str = "HEAD",
    validation_profile: ValidationProfile = ValidationProfile.STANDARD,
    allowed_paths: tuple[str, ...] = (),
    retain_worktree: bool = False,
) -> PatchValidationResult:
    """Validate one patch without mutating the original repository or branch."""
    repository_root = repository_root.resolve()
    run_id = f"phase04-{uuid.uuid4().hex[:12]}"
    safety = inspect_unified_patch(patch_text, allowed_paths)
    common = {
        "run_id": run_id,
        "repository_root": str(repository_root),
        "base_ref": base_ref,
        "validation_profile": validation_profile,
        "patch_safety": safety,
    }
    if not safety.accepted:
        return PatchValidationResult(
            **common,
            status=PatchValidationStatus.PATCH_REJECTED,
            failure_detail="; ".join(safety.rejection_reasons),
        )
    if not repository_root.is_dir():
        return PatchValidationResult(
            **common,
            status=PatchValidationStatus.INVALID_REQUEST,
            failure_detail="Repository root does not exist",
        )
    if not _git_available(repository_root):
        return PatchValidationResult(
            **common,
            status=PatchValidationStatus.GIT_UNAVAILABLE,
            failure_detail="Git is unavailable or repository root is not a worktree",
        )
    if not _safe_base_ref(repository_root, base_ref):
        return PatchValidationResult(
            **common,
            status=PatchValidationStatus.INVALID_REQUEST,
            failure_detail="Base ref does not resolve to a commit",
        )

    temp_root = Path(tempfile.mkdtemp(prefix="storefront-guard-phase04-"))
    worktree = temp_root / "worktree"
    patch_file = temp_root / "candidate.patch"
    patch_file.write_text(patch_text, encoding="utf-8", newline="\n")
    command_results: list[ValidationCommandResult] = []
    status = PatchValidationStatus.VALIDATED
    failure_detail = ""
    worktree_created = False

    try:
        create = _named(
            _run(
                ("git", "worktree", "add", "--detach", str(worktree), base_ref),
                repository_root,
                60,
            ),
            "worktree_create",
        )
        command_results.append(create)
        if not create.passed:
            status = PatchValidationStatus.WORKTREE_CREATE_FAILED
            failure_detail = "Detached validation worktree could not be created"
        else:
            worktree_created = True

        if status is PatchValidationStatus.VALIDATED:
            apply_check = _named(
                _run(
                    ("git", "apply", "--check", "--whitespace=error", "--recount", str(patch_file)),
                    worktree,
                    60,
                ),
                "patch_apply_check",
            )
            command_results.append(apply_check)
            if not apply_check.passed:
                status = PatchValidationStatus.PATCH_APPLY_FAILED
                failure_detail = "Patch does not apply cleanly to detached worktree"

        if status is PatchValidationStatus.VALIDATED:
            apply = _named(
                _run(
                    ("git", "apply", "--whitespace=error", "--recount", str(patch_file)),
                    worktree,
                    60,
                ),
                "patch_apply",
            )
            command_results.append(apply)
            if not apply.passed:
                status = PatchValidationStatus.PATCH_APPLY_FAILED
                failure_detail = "Patch application failed after a successful preflight"

        if status is PatchValidationStatus.VALIDATED:
            for name, command in _validation_commands(validation_profile):
                checked = _named(_run(command, worktree), name)
                command_results.append(checked)
                if not checked.passed:
                    status = PatchValidationStatus.VALIDATION_FAILED
                    failure_detail = f"Allowlisted validation command failed: {name}"
                    break
    finally:
        worktree_retained = retain_worktree and worktree_created
        if worktree_created and not retain_worktree:
            cleanup = _named(
                _run(("git", "worktree", "remove", "--force", str(worktree)), repository_root, 60),
                "worktree_cleanup",
            )
            command_results.append(cleanup)
            if not cleanup.passed and status is PatchValidationStatus.VALIDATED:
                status = PatchValidationStatus.CLEANUP_FAILED
                failure_detail = "Validation passed but the temporary worktree could not be removed"
        if not retain_worktree:
            shutil.rmtree(temp_root, ignore_errors=True)

    return PatchValidationResult(
        **common,
        status=status,
        command_results=tuple(command_results),
        worktree_retained=worktree_retained,
        retained_worktree_path=str(worktree) if worktree_retained else "",
        failure_detail=failure_detail,
    )


def write_validation_artifact(result: PatchValidationResult, artifact_dir: Path) -> Path:
    """Write a machine-readable Phase 04 result without embedding the patch."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / f"{result.run_id}.validation.json"
    artifact_path.write_text(
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact_path
