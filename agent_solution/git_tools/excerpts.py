"""Safe bounded file excerpt collection.

Reads eligible text files within configured limits, never loading
binary or sensitive content into evidence text.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from agent_solution.git_tools.models import (
    ChangedFile,
    CollectionLimits,
    ExcludedArtifact,
    FileExcerpt,
    StagingStatus,
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_text_eligible(cf: ChangedFile) -> bool:
    """Determine if a changed file is eligible for excerpt collection."""
    if cf.is_binary:
        return False
    if cf.is_sensitive:
        return False
    if not cf.exists_on_disk:
        return False
    if not cf.is_regular_file:
        return False
    if not cf.eligible_for_excerpt:
        return False
    return True


def _read_bounded(
    path: Path,
    max_bytes: int,
) -> tuple[str, bool]:
    """Read a file with byte-level truncation.

    Returns (text, truncated).
    """
    try:
        raw = path.read_bytes()
    except (OSError, PermissionError):
        return "", False

    if len(raw) > max_bytes:
        raw = raw[:max_bytes]
        return raw.decode("utf-8", errors="replace"), True

    return raw.decode("utf-8", errors="replace"), False


def collect_excerpts(
    changed_files: tuple[ChangedFile, ...],
    repository_root: Path,
    limits: CollectionLimits,
) -> tuple[tuple[FileExcerpt, ...], tuple[ExcludedArtifact, ...]]:
    """Collect bounded excerpts from eligible changed files.

    Returns (excerpts, excluded_artifacts).
    """
    excerpts: list[FileExcerpt] = []
    excluded: list[ExcludedArtifact] = []
    total_bytes = 0
    files_collected = 0

    for cf in changed_files:
        if not _is_text_eligible(cf):
            if cf.is_binary:
                excluded.append(
                    ExcludedArtifact(
                        relative_path=cf.relative_path,
                        exclusion_reason="binary_artifact",
                        size_bytes=cf.size_bytes,
                        is_binary=True,
                        is_sensitive=False,
                    )
                )
            elif cf.is_sensitive:
                excluded.append(
                    ExcludedArtifact(
                        relative_path=cf.relative_path,
                        exclusion_reason="sensitive_artifact",
                        size_bytes=cf.size_bytes,
                        is_binary=False,
                        is_sensitive=True,
                    )
                )
            elif not cf.exists_on_disk:
                excluded.append(
                    ExcludedArtifact(
                        relative_path=cf.relative_path,
                        exclusion_reason="file_not_on_disk",
                        size_bytes=cf.size_bytes,
                        is_binary=False,
                        is_sensitive=False,
                    )
                )
            continue

        if files_collected >= limits.max_excerpt_files:
            excluded.append(
                ExcludedArtifact(
                    relative_path=cf.relative_path,
                    exclusion_reason="excerpt_file_limit_reached",
                    size_bytes=cf.size_bytes,
                    is_binary=False,
                    is_sensitive=False,
                )
            )
            continue

        remaining_bytes = limits.max_total_excerpt_bytes - total_bytes
        if remaining_bytes <= 0:
            excluded.append(
                ExcludedArtifact(
                    relative_path=cf.relative_path,
                    exclusion_reason="total_excerpt_byte_limit_reached",
                    size_bytes=cf.size_bytes,
                    is_binary=False,
                    is_sensitive=False,
                )
            )
            continue

        file_path = repository_root / cf.relative_path
        per_file_limit = min(
            limits.max_excerpt_bytes_per_file, remaining_bytes
        )
        text, truncated = _read_bounded(file_path, per_file_limit)

        if not text:
            continue

        lines = text.split("\n")
        line_count = len(lines)

        excerpt = FileExcerpt(
            relative_path=cf.relative_path,
            start_line=1,
            end_line=line_count,
            text=text,
            byte_count=len(text.encode("utf-8")),
            truncated=truncated,
            sha256_of_captured_text=_sha256_text(text),
            source_reason="changed_file_in_scope",
        )
        excerpts.append(excerpt)
        total_bytes += excerpt.byte_count
        files_collected += 1

    return tuple(excerpts), tuple(excluded)
