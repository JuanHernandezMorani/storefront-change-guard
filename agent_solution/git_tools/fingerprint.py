"""Repository fingerprinting for cache invalidation.

Produces a deterministic fingerprint from Git state that a later cache
layer can use to reject reuse when the snapshot is incomplete.
"""

from __future__ import annotations

import hashlib

from agent_solution.git_tools.models import (
    CollectionLimits,
    DiffArtifact,
    RepositoryFingerprint,
)


def _sha256_bytes(data: bytes) -> str:
    """Return hex SHA-256 of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def _sha256_text(text: str) -> str:
    """Return hex SHA-256 of UTF-8 encoded text."""
    return _sha256_bytes(text.encode("utf-8"))


def compute_diff_hash(diff_artifact: DiffArtifact | None) -> str:
    """Hash a diff artifact's content, or return empty string for None."""
    if diff_artifact is None:
        return _sha256_text("")
    return diff_artifact.sha256


def compute_untracked_manifest_hash(
    untracked_paths: tuple[str, ...],
) -> str:
    """Hash the sorted manifest of untracked file paths."""
    if not untracked_paths:
        return _sha256_text("")
    combined = "\n".join(sorted(untracked_paths))
    return _sha256_text(combined)


def compute_scope_hash(
    changed_file_paths: tuple[str, ...],
) -> str:
    """Hash the sorted set of all relevant changed file paths."""
    if not changed_file_paths:
        return _sha256_text("")
    combined = "\n".join(sorted(changed_file_paths))
    return _sha256_text(combined)


def build_fingerprint(
    *,
    head_sha: str,
    staged_diff: DiffArtifact | None,
    unstaged_diff: DiffArtifact | None,
    untracked_paths: tuple[str, ...],
    changed_file_paths: tuple[str, ...],
    truncated_staged: bool = False,
    truncated_unstaged: bool = False,
    incomplete_scope: bool = False,
    excluded_reasons: tuple[str, ...] = (),
    limits: CollectionLimits | None = None,
) -> RepositoryFingerprint:
    """Build a deterministic repository fingerprint.

    The fingerprint is only marked complete when all content could be
    safely incorporated.  Any truncation, exclusion, or incomplete
    scope marks the fingerprint as incomplete for cache use.
    """
    ineligibility: list[str] = []

    if truncated_staged:
        ineligibility.append("staged_diff_truncated")
    if truncated_unstaged:
        ineligibility.append("unstaged_diff_truncated")
    if incomplete_scope:
        ineligibility.append("scope_incomplete")
    ineligibility.extend(excluded_reasons)

    is_complete = len(ineligibility) == 0

    return RepositoryFingerprint(
        head_sha=head_sha,
        staged_diff_hash=compute_diff_hash(staged_diff),
        unstaged_diff_hash=compute_diff_hash(unstaged_diff),
        untracked_manifest_hash=compute_untracked_manifest_hash(untracked_paths),
        relevant_scope_hash=compute_scope_hash(changed_file_paths),
        fingerprint_schema_version="0.1.0",
        is_complete_for_cache=is_complete,
        cache_ineligibility_reasons=tuple(ineligibility),
    )
