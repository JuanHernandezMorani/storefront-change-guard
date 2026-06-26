"""Git context data contracts.

All Git context decisions are encoded as explicit enum values and frozen
dataclasses.  Prose is never the sole carrier of evidence decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class GitContextStatus(StrEnum):
    """Outcome status for Git context collection."""

    COLLECTED = "COLLECTED"
    NO_ACTIONABLE_DIFF = "NO_ACTIONABLE_DIFF"
    NOT_A_GIT_REPOSITORY = "NOT_A_GIT_REPOSITORY"
    GIT_UNAVAILABLE = "GIT_UNAVAILABLE"
    GIT_COMMAND_TIMEOUT = "GIT_COMMAND_TIMEOUT"
    GIT_COMMAND_FAILED = "GIT_COMMAND_FAILED"
    INVALID_EXPLICIT_PATH = "INVALID_EXPLICIT_PATH"
    PATH_ESCAPES_REPOSITORY = "PATH_ESCAPES_REPOSITORY"
    INTAKE_DECISION_BLOCKED = "INTAKE_DECISION_BLOCKED"
    COLLECTION_LIMIT_REACHED = "COLLECTION_LIMIT_REACHED"


class ChangeKind(StrEnum):
    """How a file was changed."""

    ADDED = "A"
    COPIED = "C"
    DELETED = "D"
    MODIFIED = "M"
    RENAMED = "R"
    TYPE_CHANGE = "T"
    UNMERGED = "U"
    UNKNOWN = "X"


class StagingStatus(StrEnum):
    """Whether a change is staged, unstaged, or untracked."""

    STAGED = "staged"
    UNSTAGED = "unstaged"
    UNTRACKED = "untracked"


class ScopeMode(StrEnum):
    """Resolved scope mode from Phase 2A intake."""

    WORKING_TREE_DIFF = "working_tree_diff"
    EXPLICIT_PATHS = "explicit_paths"
    BOUNDED_REPOSITORY_SEARCH = "bounded_repository_search"
    NO_ACTIONABLE_SCOPE = "no_actionable_scope"


# ---------------------------------------------------------------------------
# Collection limits
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class CollectionLimits:
    """Configurable bounds for evidence collection."""

    max_changed_files: int = 100
    max_excerpt_files: int = 8
    max_excerpt_bytes_per_file: int = 65536
    max_total_excerpt_bytes: int = 262144
    max_diff_capture_bytes: int = 524288
    max_command_output_bytes: int = 1048576
    command_timeout_seconds: int = 20


# ---------------------------------------------------------------------------
# Git command provenance
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class GitCommandEvidence:
    """Provenance record for a single Git command execution."""

    command: tuple[str, ...]
    exit_code: int
    stdout_length: int
    stderr_length: int
    timed_out: bool
    cwd: str
    duration_ms: int


# ---------------------------------------------------------------------------
# Changed file inventory
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ChangedFile:
    """Inventory entry for a single changed file."""

    relative_path: str
    change_kind: ChangeKind
    staging: StagingStatus
    exists_on_disk: bool
    is_regular_file: bool
    is_binary: bool
    is_sensitive: bool
    size_bytes: int
    extension: str
    eligible_for_excerpt: bool
    exclusion_reason: str


# ---------------------------------------------------------------------------
# Diff artifact
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class DiffArtifact:
    """Captured diff with provenance and bounds."""

    diff_type: str
    text: str
    sha256: str
    byte_count: int
    truncated: bool
    captured_limit: int
    file_count: int


# ---------------------------------------------------------------------------
# File excerpt
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class FileExcerpt:
    """Bounded excerpt from a text file."""

    relative_path: str
    start_line: int
    end_line: int
    text: str
    byte_count: int
    truncated: bool
    sha256_of_captured_text: str
    source_reason: str


# ---------------------------------------------------------------------------
# Excluded artifact
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ExcludedArtifact:
    """Record of a file excluded from evidence collection."""

    relative_path: str
    exclusion_reason: str
    size_bytes: int
    is_binary: bool
    is_sensitive: bool


# ---------------------------------------------------------------------------
# Repository fingerprint
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class RepositoryFingerprint:
    """Deterministic fingerprint for cache invalidation."""

    head_sha: str
    staged_diff_hash: str
    unstaged_diff_hash: str
    untracked_manifest_hash: str
    relevant_scope_hash: str
    fingerprint_schema_version: str = "0.1.0"
    is_complete_for_cache: bool = True
    cache_ineligibility_reasons: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Top-level Git context snapshot
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class GitContextSnapshot:
    """Complete deterministic evidence snapshot from Git context collection.

    This is the authoritative evidence record produced by Phase 2B.
    """

    status: GitContextStatus
    repository_root: str
    repository_relative_root: str
    head_sha: str
    branch_name_or_detached_state: str
    status_porcelain: str
    staged_change_count: int
    unstaged_change_count: int
    untracked_change_count: int
    changed_files: tuple[ChangedFile, ...]
    staged_diff: DiffArtifact | None
    unstaged_diff: DiffArtifact | None
    file_excerpts: tuple[FileExcerpt, ...]
    excluded_artifacts: tuple[ExcludedArtifact, ...]
    repository_fingerprint: RepositoryFingerprint
    collection_limits: CollectionLimits
    collection_warnings: tuple[str, ...]
    command_evidence: tuple[GitCommandEvidence, ...]
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
