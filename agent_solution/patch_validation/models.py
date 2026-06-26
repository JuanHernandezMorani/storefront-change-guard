"""Strict data contracts for Phase 04 isolated patch validation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class PatchValidationStatus(StrEnum):
    """Terminal status for a deterministic patch-validation run."""

    VALIDATED = "VALIDATED"
    INVALID_REQUEST = "INVALID_REQUEST"
    PATCH_REJECTED = "PATCH_REJECTED"
    GIT_UNAVAILABLE = "GIT_UNAVAILABLE"
    WORKTREE_CREATE_FAILED = "WORKTREE_CREATE_FAILED"
    PATCH_APPLY_FAILED = "PATCH_APPLY_FAILED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    CLEANUP_FAILED = "CLEANUP_FAILED"


class ValidationProfile(StrEnum):
    """Named deterministic command profiles; raw shell commands are forbidden."""

    STANDARD = "standard"
    GIT_DIFF_CHECK = "git_diff_check"


@dataclass(frozen=True, slots=True)
class PatchSafetyReport:
    """Result of static unified-diff safety validation."""

    accepted: bool
    patch_sha256: str
    patch_byte_count: int
    changed_paths: tuple[str, ...]
    rejection_reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ValidationCommandResult:
    """Bounded execution record for a fixed allowlisted validation command."""

    name: str
    command: tuple[str, ...]
    exit_code: int
    timed_out: bool
    duration_ms: int
    stdout_excerpt: str
    stderr_excerpt: str

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


@dataclass(frozen=True, slots=True)
class PatchValidationResult:
    """Machine-readable outcome for a worktree-only validation run."""

    run_id: str
    status: PatchValidationStatus
    repository_root: str
    base_ref: str
    validation_profile: ValidationProfile
    patch_safety: PatchSafetyReport
    command_results: tuple[ValidationCommandResult, ...] = ()
    worktree_retained: bool = False
    retained_worktree_path: str = ""
    artifact_path: str = ""
    failure_detail: str = ""
    created_at_utc: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe artifact without a raw patch or model output."""
        data = asdict(self)
        data["status"] = self.status.value
        data["validation_profile"] = self.validation_profile.value
        data["command_results"] = [
            {
                **asdict(command),
                "command": list(command.command),
                "passed": command.passed,
            }
            for command in self.command_results
        ]
        data["patch_safety"]["changed_paths"] = list(self.patch_safety.changed_paths)
        data["patch_safety"]["rejection_reasons"] = list(self.patch_safety.rejection_reasons)
        return data
