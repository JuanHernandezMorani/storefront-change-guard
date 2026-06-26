# Phase 2B — Git Context Collection and Deterministic Evidence Snapshot

## Purpose

Phase 2B transforms an accepted or refined intake contract (from Phase 2A) into a structured, bounded, read-only repository evidence snapshot.  It provides deterministic Git context that later phases (3 and 4) can safely consume without model calls, repository mutation, or arbitrary command execution.

## Architecture

```
user request
→ Phase 2A intake decision (IntakeContract)
→ Phase 2B Git context collection (GitContextSnapshot)
→ Phase 3 grounded semantic analysis (deferred)
→ Phase 4 isolated patch proposal (deferred)
```

Phase 2B consumes the Phase 2A `IntakeContract` conservatively.  It preserves the original intake contract unchanged and produces a separate `GitContextSnapshot`.

## Core Safety Requirements

All Git commands:

- Use `subprocess` with argument arrays
- Use `shell=False`
- Use a resolved repository root as `cwd`
- Use explicit timeouts
- Capture stdout/stderr safely
- Record command provenance
- Never execute arbitrary user-provided command text
- Never invoke hooks, external diff tooling, or destructive operations
- Use `--no-ext-diff` and `--no-color` where relevant

## Git Command Allowlist

Phase 2B only executes these Git commands:

| Command | Purpose |
|---|---|
| `git rev-parse --show-toplevel` | Validate repository root |
| `git rev-parse HEAD` | Capture HEAD SHA |
| `git branch --show-current` | Capture branch name |
| `git status --porcelain=v1 -z` | Count staged/unstaged/untracked changes |
| `git diff --cached --name-status` | List staged changed files |
| `git diff --name-status` | List unstaged changed files |
| `git ls-files --others --exclude-standard` | List untracked files |
| `git diff --cached --unified=3` | Capture staged diff |
| `git diff --unified=3` | Capture unstaged diff |

**Prohibited commands:** `git commit`, `git reset`, `git checkout`, `git restore`, `git clean`, `git add`, `git merge`, `git rebase`, `git push`, `git pull`, `git gc`, `git config --global`.

## Data Contracts

### GitContextStatus

Outcome status for collection:

- `COLLECTED` — evidence successfully captured
- `NO_ACTIONABLE_DIFF` — no staged, unstaged, or eligible untracked changes
- `NOT_A_GIT_REPOSITORY` — path is not a Git repository
- `GIT_UNAVAILABLE` — Git binary not found
- `GIT_COMMAND_TIMEOUT` — command exceeded timeout
- `GIT_COMMAND_FAILED` — command returned non-zero exit
- `INVALID_EXPLICIT_PATH` — explicit path does not exist
- `PATH_ESCAPES_REPOSITORY` — path traversal detected
- `INTAKE_DECISION_BLOCKED` — intake decision blocks collection
- `COLLECTION_LIMIT_REACHED` — a configurable limit was hit

### Scope Modes

| Mode | Behavior |
|---|---|
| `working_tree_diff` | Collect only changed tracked files plus eligible untracked files |
| `explicit_paths` | Collect only the specified paths (validated against traversal) |
| `bounded_repository_search` | Prepare bounded inventory contract for Phase 3 (no content collection) |
| `no_actionable_scope` | Return structured no-op |

### ChangedFile

For every discovered changed file:

- `relative_path`, `change_kind`, `staging` (staged/unstaged/untracked)
- `exists_on_disk`, `is_regular_file`, `is_binary`, `is_sensitive`
- `size_bytes`, `extension`, `eligible_for_excerpt`, `exclusion_reason`

### DiffArtifact

- `diff_type`, `text`, `sha256`, `byte_count`
- `truncated`, `captured_limit`, `file_count`

### FileExcerpt

- `relative_path`, `start_line`, `end_line`, `text`
- `byte_count`, `truncated`, `sha256_of_captured_text`, `source_reason`

### ExcludedArtifact

- `relative_path`, `exclusion_reason`, `size_bytes`, `is_binary`, `is_sensitive`

### RepositoryFingerprint

For cache invalidation:

- `head_sha`, `staged_diff_hash`, `unstaged_diff_hash`
- `untracked_manifest_hash`, `relevant_scope_hash`
- `fingerprint_schema_version`, `is_complete_for_cache`
- `cache_ineligibility_reasons`

### CollectionLimits

Configurable bounds:

| Limit | Default | Description |
|---|---|---|
| `max_changed_files` | 100 | Maximum changed files to inventory |
| `max_excerpt_files` | 8 | Maximum files to excerpt |
| `max_excerpt_bytes_per_file` | 65,536 | Maximum bytes per file excerpt |
| `max_total_excerpt_bytes` | 262,144 | Maximum aggregate excerpt bytes |
| `max_diff_capture_bytes` | 524,288 | Maximum diff text to capture |
| `max_command_output_bytes` | 1,048,576 | Maximum command output to capture |
| `command_timeout_seconds` | 20 | Per-command timeout |

## Sensitive/Binary/Oversized Handling

### Sensitive Files

Excluded from excerpt collection by conservative basename and extension checks:

- `.env`, `.env.*`
- `*.pem`, `*.key`, `*.pfx`, `*.p12`
- `id_rsa`, `id_ed25519`, `id_ecdsa`
- `credentials*`, `secrets*`, `token*`

Sensitive files are recorded in `excluded_artifacts` with `is_sensitive=True` and `exclusion_reason="sensitive_artifact"`.

### Binary Files

Detected by file content.  Excluded from excerpt collection.  Recorded with `is_binary=True` and `exclusion_reason="binary_artifact"`.

### Oversized Artifacts

When a diff exceeds `max_diff_capture_bytes`:
- A bounded excerpt is preserved
- `truncated=True` is recorded
- The fingerprint is marked incomplete for cache

When total excerpts exceed limits:
- Remaining files are excluded with explicit reasons
- The fingerprint is marked incomplete

## Fingerprint Completeness and Cache Safety

The repository fingerprint is only marked `is_complete_for_cache=True` when:
- No diff was truncated
- No relevant scope was incomplete
- No sensitive or binary artifacts were excluded from the scope

When any condition fails:
- `is_complete_for_cache=False`
- Each reason is recorded in `cache_ineligibility_reasons`
- A later cache layer **must** reject reuse

**Rule:** Never create a misleading partial cache key.  A partial fingerprint is explicitly marked incomplete.

## Intake Integration

Phase 2B respects the Phase 2A intake decision:

| Intake Decision | Phase 2B Behavior |
|---|---|
| `ACCEPT_WITH_SAFE_DEFAULTS` + `working_tree_diff` | Collect only current changed-file evidence |
| `REFINE_FOR_EXECUTION` | Collect only the explicitly resolved scope |
| `CLARIFY` | Return `INTAKE_DECISION_BLOCKED` — no collection |
| `REJECT_UNSAFE_OR_UNSUPPORTED` | Return `INTAKE_DECISION_BLOCKED` — no collection |

The execution contract and Git context snapshot remain distinct typed objects.

## Relationship to Phase 3

Phase 3 (Grounded Analysis) will consume the `GitContextSnapshot` for semantic review.  Phase 2B provides:
- Scoped changed-file inventory
- Bounded file excerpts
- Repository fingerprint for cache coordination
- Deterministic evidence with explicit provenance

Phase 3 must not assume the snapshot is complete for cache unless `is_complete_for_cache=True`.

## Relationship to Phase 4

Phase 4 (Isolated Patch Validation) will use the Git context for:
- Verifying patch scope against changed files
- Validating worktree isolation
- Confirming no unintended scope expansion

Phase 2B preserves the worktree-only invariant as a constraint in the execution brief.

## Known Limitations

1. **Binary detection is conservative:** Files are classified as binary based on content, which may not catch all binary formats.
2. **Sensitive detection is pattern-based:** Uses basename and extension matching, not content inspection.
3. **Bounded excerpts are line-based:** Excerpts start at line 1; selective line ranges are not yet supported.
4. **No semantic search:** `BOUNDED_REPOSITORY_SEARCH` mode prepares an inventory contract but does not collect repository content.  This is deferred to Phase 3.
5. **Fingerprint incompletion:** When diffs are truncated or files are excluded, the fingerprint is correctly marked incomplete, but this means cache reuse is disabled for those states.

## Deferred Validation Status

All test fixtures are implemented and passing.  The implementation is internally validated pending `Phase-02-REVIEW-02`.
