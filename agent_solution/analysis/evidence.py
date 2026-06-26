"""Evidence bundle builder.

Constructs bounded evidence bundles from Phase 2 intake contracts and
Git context snapshots. Performs one deterministic evidence-expansion pass before
model invocation.

Explicit file targets are an authority boundary, not a hint. When the request
names a concrete eligible file, Phase 03 uses that target as the review scope
and deliberately excludes unrelated working-tree diff artifacts. This prevents
an in-progress implementation diff from crowding out the file the user asked
to review.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from agent_solution.analysis.models import (
    EvidenceBundle,
    EvidenceRecord,
    Phase3Limits,
    SourceKind,
)
from agent_solution.git_tools.models import GitContextSnapshot
from agent_solution.intake.models import IntakeContract, IntakeDecision, TaskType

# Eligible text file extensions for explicit file evidence
_ELIGIBLE_EXTENSIONS: frozenset[str] = frozenset({
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
    ".c", ".cpp", ".h", ".hpp", ".rb", ".php", ".swift", ".kt",
    ".sh", ".bash", ".zsh", ".ps1", ".yaml", ".yml", ".toml",
    ".json", ".xml", ".md", ".txt", ".cfg", ".ini", ".env",
})

# A concrete path is sufficient evidence scope for these non-mutating Phase 03
# requests. It intentionally constrains collection to the named file(s).
_EXPLICIT_TARGET_SCOPE_TASKS: frozenset[TaskType] = frozenset({
    TaskType.CODE_REVIEW,
    TaskType.BUG_DIAGNOSIS,
    TaskType.CODEBASE_QUESTION,
})


def _sha256_text(text: str) -> str:
    """Return hex SHA-256 of UTF-8 encoded text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _make_evidence_id(index: int) -> str:
    """Generate stable evidence ID."""
    return f"E{index + 1}"


def _truncate_content(content: str, max_bytes: int) -> tuple[str, bool]:
    """Truncate content to byte limit."""
    encoded = content.encode("utf-8")
    if len(encoded) <= max_bytes:
        return content, False
    truncated = encoded[:max_bytes].decode("utf-8", errors="replace")
    return truncated, True


class EvidenceBundleBuilder:
    """Build bounded evidence bundles from Phase 2 outputs.

    Consumes IntakeContract and GitContextSnapshot without modifying them.
    Performs one deterministic expansion pass within Phase 2 scope.
    """

    def __init__(self, limits: Phase3Limits | None = None):
        self._limits = limits or Phase3Limits()

    @staticmethod
    def _explicit_targets(intake: IntakeContract) -> tuple[str, ...]:
        scope = intake.resolved_scope
        targets = getattr(scope, "explicit_file_targets", ())
        return tuple(targets)

    def _append_explicit_target_records(
        self,
        *,
        intake: IntakeContract,
        repository_root: Path,
        targets: tuple[str, ...],
        evidence_records: list[EvidenceRecord],
        excluded_records: list[EvidenceRecord],
        limitations: list[str],
        start_index: int,
    ) -> int:
        """Append full-file evidence for explicit, eligible targets.

        The full target file is the authoritative review evidence. It is
        collected before generic diff/excerpt sources so a broad unrelated
        working-tree change cannot displace an explicitly requested file.
        """
        index = start_index
        for target_path in targets:
            if index >= self._limits.max_evidence_records:
                limitations.append("Evidence record limit reached")
                break

            target_file = repository_root / target_path
            if not target_file.exists() or not target_file.is_file():
                continue

            if target_file.suffix.lower() not in _ELIGIBLE_EXTENSIONS:
                excluded_records.append(
                    EvidenceRecord(
                        evidence_id=_make_evidence_id(index),
                        source_kind=SourceKind.FILE_EXCERPT,
                        relative_path=target_path,
                        start_line=0,
                        end_line=0,
                        content="",
                        content_sha256="",
                        byte_count=0,
                        selection_reason="ineligible_extension",
                        provenance=f"excluded: {target_path}",
                    )
                )
                index += 1
                continue

            try:
                content = target_file.read_text(encoding="utf-8", errors="replace")
            except (OSError, PermissionError):
                continue

            if not content:
                continue

            original_line_count = content.count("\n") + 1
            content, truncated = _truncate_content(
                content,
                self._limits.max_single_evidence_bytes,
            )
            if truncated:
                limitations.append(
                    f"Explicit target {target_path} truncated to evidence byte limit"
                )

            evidence_records.append(
                EvidenceRecord(
                    evidence_id=_make_evidence_id(index),
                    source_kind=SourceKind.EXPLICIT_PATH,
                    relative_path=target_path,
                    start_line=1,
                    end_line=original_line_count,
                    content=content,
                    content_sha256=_sha256_text(content),
                    byte_count=len(content.encode("utf-8")),
                    selection_reason=(
                        f"explicit_target_for_{intake.detected_task_type.value.lower()}"
                    ),
                    provenance=f"explicit file target: {target_path}",
                )
            )
            index += 1

        return index

    def _append_diff_artifacts(
        self,
        *,
        git_snapshot: GitContextSnapshot,
        evidence_records: list[EvidenceRecord],
        limitations: list[str],
        start_index: int,
    ) -> int:
        """Append generic staged and unstaged diff artifacts."""
        index = start_index

        if git_snapshot.staged_diff and git_snapshot.staged_diff.text:
            content, truncated = _truncate_content(
                git_snapshot.staged_diff.text,
                self._limits.max_single_evidence_bytes,
            )
            if truncated:
                limitations.append("Staged diff truncated to evidence byte limit")

            evidence_records.append(
                EvidenceRecord(
                    evidence_id=_make_evidence_id(index),
                    source_kind=SourceKind.DIFF_ARTIFACT,
                    relative_path="(staged diff)",
                    start_line=1,
                    end_line=content.count("\n") + 1,
                    content=content,
                    content_sha256=_sha256_text(content),
                    byte_count=len(content.encode("utf-8")),
                    selection_reason="staged_diff_in_scope",
                    provenance="git diff --cached",
                )
            )
            index += 1

        if (
            index < self._limits.max_evidence_records
            and git_snapshot.unstaged_diff
            and git_snapshot.unstaged_diff.text
        ):
            content, truncated = _truncate_content(
                git_snapshot.unstaged_diff.text,
                self._limits.max_single_evidence_bytes,
            )
            if truncated:
                limitations.append("Unstaged diff truncated to evidence byte limit")

            evidence_records.append(
                EvidenceRecord(
                    evidence_id=_make_evidence_id(index),
                    source_kind=SourceKind.DIFF_ARTIFACT,
                    relative_path="(unstaged diff)",
                    start_line=1,
                    end_line=content.count("\n") + 1,
                    content=content,
                    content_sha256=_sha256_text(content),
                    byte_count=len(content.encode("utf-8")),
                    selection_reason="unstaged_diff_in_scope",
                    provenance="git diff",
                )
            )
            index += 1

        return index

    def _append_file_excerpts(
        self,
        *,
        git_snapshot: GitContextSnapshot,
        evidence_records: list[EvidenceRecord],
        limitations: list[str],
        start_index: int,
    ) -> int:
        """Append bounded excerpts for generic diff-scoped requests."""
        index = start_index
        for excerpt in git_snapshot.file_excerpts:
            if index >= self._limits.max_evidence_records:
                limitations.append("Evidence record limit reached")
                break

            content, truncated = _truncate_content(
                excerpt.text,
                self._limits.max_single_evidence_bytes,
            )
            if truncated:
                limitations.append(f"Excerpt {excerpt.relative_path} truncated")

            evidence_records.append(
                EvidenceRecord(
                    evidence_id=_make_evidence_id(index),
                    source_kind=SourceKind.FILE_EXCERPT,
                    relative_path=excerpt.relative_path,
                    start_line=excerpt.start_line,
                    end_line=excerpt.end_line,
                    content=content,
                    content_sha256=_sha256_text(content),
                    byte_count=len(content.encode("utf-8")),
                    selection_reason=excerpt.source_reason,
                    provenance=(
                        f"file excerpt: {excerpt.relative_path}:"
                        f"{excerpt.start_line}-{excerpt.end_line}"
                    ),
                )
            )
            index += 1

        return index

    def build(
        self,
        analysis_request_id: str,
        intake: IntakeContract,
        git_snapshot: GitContextSnapshot,
        repository_root: Path,
    ) -> EvidenceBundle | None:
        """Build an evidence bundle from Phase 2 outputs.

        Returns an EvidenceBundle on success, or None when no eligible evidence
        can be collected. Explicit file targets dominate generic diff evidence.
        """
        if intake.decision in (
            IntakeDecision.CLARIFY,
            IntakeDecision.REJECT_UNSAFE_OR_UNSUPPORTED,
        ):
            return None

        blocked_statuses = (
            "INTAKE_DECISION_BLOCKED",
            "NOT_A_GIT_REPOSITORY",
            "GIT_UNAVAILABLE",
        )
        if git_snapshot.status.value in blocked_statuses:
            return None

        evidence_records: list[EvidenceRecord] = []
        excluded_records: list[EvidenceRecord] = []
        limitations: list[str] = []
        index = 0

        explicit_targets = self._explicit_targets(intake)
        target_scoped_request = (
            bool(explicit_targets)
            and intake.detected_task_type in _EXPLICIT_TARGET_SCOPE_TASKS
        )

        if target_scoped_request:
            index = self._append_explicit_target_records(
                intake=intake,
                repository_root=repository_root,
                targets=explicit_targets,
                evidence_records=evidence_records,
                excluded_records=excluded_records,
                limitations=limitations,
                start_index=index,
            )

            if (
                (git_snapshot.staged_diff and git_snapshot.staged_diff.text)
                or (git_snapshot.unstaged_diff and git_snapshot.unstaged_diff.text)
                or git_snapshot.file_excerpts
            ):
                limitations.append(
                    "Generic working-tree evidence omitted because explicit file "
                    "targets define the Phase 03 scope."
                )
        else:
            index = self._append_diff_artifacts(
                git_snapshot=git_snapshot,
                evidence_records=evidence_records,
                limitations=limitations,
                start_index=index,
            )
            index = self._append_file_excerpts(
                git_snapshot=git_snapshot,
                evidence_records=evidence_records,
                limitations=limitations,
                start_index=index,
            )

        if (
            intake.detected_task_type == TaskType.CODEBASE_QUESTION
            and not target_scoped_request
            and index < self._limits.max_evidence_records
        ):
            search_records = self._bounded_search(
                intake.normalized_request,
                repository_root,
                git_snapshot,
                start_index=index,
                limits=self._limits,
            )
            evidence_records.extend(search_records)
            index += len(search_records)

        total_bytes = sum(record.byte_count for record in evidence_records)
        if total_bytes > self._limits.max_total_evidence_bytes:
            limitations.append(
                f"Total evidence bytes ({total_bytes}) exceeds limit "
                f"({self._limits.max_total_evidence_bytes}). Truncating."
            )
            evidence_records = self._truncate_to_byte_limit(
                evidence_records,
                self._limits.max_total_evidence_bytes,
            )
            total_bytes = sum(record.byte_count for record in evidence_records)

        if not evidence_records:
            if explicit_targets:
                limitations.append(
                    f"Explicit file targets {explicit_targets} yielded no eligible evidence"
                )
            return None

        bundle_content = "|".join(record.content_sha256 for record in evidence_records)
        bundle_sha256 = _sha256_text(bundle_content)

        # Cache validity must match the evidence authority boundary.  For a
        # request that explicitly names file targets, the complete content of
        # those target files is the authoritative scope.  An unrelated large
        # working-tree diff may be truncated by Git collection, but it must not
        # disable a cache keyed from the same explicit evidence.
        explicit_target_truncated = any(
            limitation.startswith("Explicit target ")
            and "truncated to evidence byte limit" in limitation
            for limitation in limitations
        )
        explicit_targets_complete = (
            target_scoped_request
            and len(evidence_records) == len(explicit_targets)
            and not explicit_target_truncated
            and all(
                record.source_kind is SourceKind.EXPLICIT_PATH
                for record in evidence_records
            )
        )

        if explicit_targets_complete:
            scoped_identity = "|".join(
                f"{record.relative_path}:{record.content_sha256}"
                for record in evidence_records
            )
            fingerprint_str = f"explicit-scope-v1:{_sha256_text(scoped_identity)}"
            fingerprint_complete_for_cache = True
        else:
            fingerprint_str = (
                f"{git_snapshot.repository_fingerprint.head_sha}:"
                f"{git_snapshot.repository_fingerprint.staged_diff_hash}:"
                f"{git_snapshot.repository_fingerprint.unstaged_diff_hash}"
            )
            fingerprint_complete_for_cache = (
                git_snapshot.repository_fingerprint.is_complete_for_cache
            )

        return EvidenceBundle(
            analysis_request_id=analysis_request_id,
            intake_request_id=intake.request_id,
            repository_fingerprint=fingerprint_str,
            repository_fingerprint_complete_for_cache=fingerprint_complete_for_cache,
            task_type=intake.detected_task_type.value,
            requested_output_language="auto",
            evidence_bundle_schema_version="0.3.1",
            evidence_records=tuple(evidence_records),
            excluded_evidence_records=tuple(excluded_records),
            bundle_byte_count=total_bytes,
            bundle_sha256=bundle_sha256,
            collection_limitations=tuple(limitations),
        )

    def _bounded_search(
        self,
        query: str,
        repository_root: Path,
        git_snapshot: GitContextSnapshot,
        start_index: int,
        limits: Phase3Limits,
    ) -> list[EvidenceRecord]:
        """Perform bounded deterministic literal search within allowed inventory.

        No semantic embeddings.  No unrestricted recursive file dumping.
        Searches eligible repository files for literal term matches.
        """
        records: list[EvidenceRecord] = []
        index = start_index

        # Normalize search terms
        terms = [t.lower() for t in query.split() if len(t) > 2]
        if not terms:
            return records

        # Build eligible file inventory from repository
        eligible_paths: list[str] = []

        # First: include changed files from git context
        for cf in git_snapshot.changed_files:
            if cf.eligible_for_excerpt and cf.exists_on_disk and not cf.is_binary:
                eligible_paths.append(cf.relative_path)

        # Second: scan repository for additional eligible files
        # (bounded search for CODEBASE_QUESTION)
        excluded_dirs = {
            ".git", "__pycache__", ".venv", "node_modules",
            ".ruff_cache", ".pytest_cache",
        }
        excluded_suffixes = {
            ".pyc", ".pyo", ".so", ".dll", ".exe",
            ".gguf", ".bin", ".db", ".sqlite",
        }

        if repository_root.exists():
            for f in repository_root.rglob("*"):
                if len(eligible_paths) >= limits.max_search_results:
                    break
                if len(records) >= limits.max_evidence_records - start_index:
                    break

                # Skip directories
                if not f.is_file():
                    continue

                # Skip excluded directories
                parts = f.relative_to(repository_root).parts
                if any(p in excluded_dirs for p in parts):
                    continue

                # Skip excluded suffixes
                if f.suffix.lower() in excluded_suffixes:
                    continue

                # Skip oversized files (> 100KB)
                try:
                    size = f.stat().st_size
                    if size > 100_000 or size == 0:
                        continue
                except (OSError, PermissionError):
                    continue

                rel = str(f.relative_to(repository_root))
                if rel not in eligible_paths:
                    eligible_paths.append(rel)

        # Search within eligible files
        search_count = 0
        for rel_path in eligible_paths:
            if index >= limits.max_evidence_records:
                break
            if search_count >= limits.max_search_queries:
                break

            file_path = repository_root / rel_path
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except (OSError, PermissionError):
                continue

            # Simple literal match
            content_lower = content.lower()
            matched = any(term in content_lower for term in terms)
            if not matched:
                continue

            search_count += 1
            # Take first matching excerpt
            lines = content.split("\n")
            match_line = 0
            for i, line in enumerate(lines):
                if any(term in line.lower() for term in terms):
                    match_line = i
                    break

            start = max(0, match_line - 2)
            end = min(len(lines), match_line + 8)
            excerpt = "\n".join(lines[start:end])
            excerpt, truncated = _truncate_content(excerpt, limits.max_single_evidence_bytes)

            record = EvidenceRecord(
                evidence_id=_make_evidence_id(index),
                source_kind=SourceKind.SEARCH_RESULT,
                relative_path=rel_path,
                start_line=start + 1,
                end_line=end,
                content=excerpt,
                content_sha256=_sha256_text(excerpt),
                byte_count=len(excerpt.encode("utf-8")),
                selection_reason=f"search_match_for: {terms[0]}",
                provenance=f"bounded search in {rel_path}",
            )
            records.append(record)
            index += 1

        return records

    def _truncate_to_byte_limit(
        self,
        records: list[EvidenceRecord],
        max_bytes: int,
    ) -> list[EvidenceRecord]:
        """Truncate evidence records to fit within byte limit."""
        result: list[EvidenceRecord] = []
        total = 0
        for record in records:
            if total + record.byte_count > max_bytes:
                break
            result.append(record)
            total += record.byte_count
        return result
