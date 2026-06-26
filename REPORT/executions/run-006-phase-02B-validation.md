# Implementation Report — Phase 02B: Git Context Collection

## Scope and Ownership

Phase 2B implements Git context collection, deterministic evidence snapshot, repository fingerprinting, bounded changed-file discovery, safe excerpt collection, and evidence manifest generation.

### Allowed implementation areas

```
agent_solution/git_tools/
agent_solution/tests/test_git_context.py
docs/phase-02-git-context-collection.md
```

### Excluded areas

No modifications to:
- Benchmarks, benchmark results, Test 1, Test 2 evidence
- Phase 1 artifacts
- Existing Phase 2A intake implementation
- Historical reports or review findings

## Architecture and Data Contracts

### Module structure

| Module | Responsibility |
|---|---|
| `agent_solution/git_tools/models.py` | All typed data contracts (enums, frozen dataclasses) |
| `agent_solution/git_tools/collector.py` | Main Git context collector (orchestrator) |
| `agent_solution/git_tools/fingerprint.py` | Repository fingerprint computation |
| `agent_solution/git_tools/excerpts.py` | Safe bounded file excerpt collection |

### Data contracts created

- `GitContextStatus` — 10 enum values for collection outcomes
- `ChangeKind` — Git change type codes (A, C, D, M, R, T, U, X)
- `StagingStatus` — staged/unstaged/untracked
- `ScopeMode` — working_tree_diff/explicit_paths/bounded_repository_search/no_actionable_scope
- `CollectionLimits` — 7 configurable bounds with defaults
- `GitCommandEvidence` — command provenance record
- `ChangedFile` — per-file inventory entry (12 fields)
- `DiffArtifact` — captured diff with SHA-256 and truncation tracking
- `FileExcerpt` — bounded text excerpt with SHA-256
- `ExcludedArtifact` — exclusion record with reason
- `RepositoryFingerprint` — cache-invalidation fingerprint (8 fields)
- `GitContextSnapshot` — top-level snapshot (20 fields)

## Git Command Allowlist

Only read-only commands are executed:

| Command | Purpose |
|---|---|
| `git rev-parse --show-toplevel` | Repository root validation |
| `git rev-parse HEAD` | HEAD SHA capture |
| `git branch --show-current` | Branch name |
| `git status --porcelain=v1 -z` | Change counting |
| `git diff --cached --name-status` | Staged file inventory |
| `git diff --name-status` | Unstaged file inventory |
| `git ls-files --others --exclude-standard` | Untracked file listing |
| `git diff --cached --unified=3` | Staged diff capture |
| `git diff --unified=3` | Unstaged diff capture |

All commands use `subprocess` with `shell=False`, argument arrays, explicit timeouts, and resolved `cwd`.

## Collection Limits

| Limit | Default | Description |
|---|---|---|
| `max_changed_files` | 100 | Changed file inventory cap |
| `max_excerpt_files` | 8 | Files eligible for excerpt |
| `max_excerpt_bytes_per_file` | 65,536 | Per-file excerpt cap |
| `max_total_excerpt_bytes` | 262,144 | Aggregate excerpt cap |
| `max_diff_capture_bytes` | 524,288 | Diff text capture cap |
| `max_command_output_bytes` | 1,048,576 | Command output cap |
| `command_timeout_seconds` | 20 | Per-command timeout |

## Sensitive/Binary/Oversized Handling

### Sensitive exclusion

Conservative basename and extension checks:
- `.env`, `.env.*`
- `*.pem`, `*.key`, `*.pfx`, `*.p12`
- `id_rsa`, `id_ed25519`, `id_ecdsa`
- `credentials*`, `secrets*`, `token*`

Recorded in `excluded_artifacts` with `is_sensitive=True`.

### Binary exclusion

Detected via content inspection before text extraction.  Excluded from excerpts, recorded with `is_binary=True`.

### Oversized handling

- Diffs exceeding `max_diff_capture_bytes`: bounded excerpt preserved, `truncated=True`, fingerprint marked incomplete
- Excerpts exceeding per-file or aggregate limits: files excluded with explicit reasons
- No silent discarding — truncation is always recorded

## Repository Fingerprint Design

The fingerprint combines:
- `head_sha` — current HEAD commit
- `staged_diff_hash` — SHA-256 of staged diff content
- `unstaged_diff_hash` — SHA-256 of unstaged diff content
- `untracked_manifest_hash` — SHA-256 of sorted untracked paths
- `relevant_scope_hash` — SHA-256 of sorted changed file paths

**Cache safety:** `is_complete_for_cache` is `True` only when no truncation, no incomplete scope, and no excluded artifacts affect the scope.  Any ineligibility reason is explicitly recorded in `cache_ineligibility_reasons`.

## Test Matrix

| # | Scenario | Expected | Status |
|---|---|---|---|
| 1 | Clean Git repository | `NO_ACTIONABLE_DIFF`, valid HEAD | PASS |
| 2 | Unstaged tracked modification | Correct inventory, unstaged diff, valid fingerprint | PASS |
| 3 | Staged tracked modification | Correct staged inventory, staged diff separate from unstaged | PASS |
| 4 | Eligible untracked text file | In inventory, fingerprint includes path | PASS |
| 5 | Sensitive `.env` file | Excluded from excerpt, explicit reason | PASS |
| 6 | Binary changed file | Excluded from excerpt, explicit classification | PASS |
| 7 | Oversized changed text file | Excerpt bounded, truncation recorded, fingerprint incomplete | PASS |
| 8 | Explicit valid path | Only that path collected | PASS |
| 9 | Explicit traversal path | Rejected with `PATH_ESCAPES_REPOSITORY` | PASS |
| 10 | Intake `CLARIFY` | `INTAKE_DECISION_BLOCKED`, no scope expansion | PASS |
| 11 | Intake `REJECT` | Blocked state | PASS |
| 12 | Deterministic fingerprint | Same fingerprint on repeated collection | PASS |
| 13 | Changed file modifies fingerprint | Fingerprint differs after modification | PASS |
| 14 | Command safety | Argument arrays, no destructive commands | PASS |
| 15 | Intake integration | CODE_REVIEW with diff reaches snapshot; no-diff stays non-actionable | PASS |
| 16 | Not a git repository | `NOT_A_GIT_REPOSITORY` | PASS |
| 17 | Sensitive `.key` file | Excluded | PASS |
| 18 | Spanish intake integration | Working-tree diff collected | PASS |

## Validation Results

| Command | Result |
|---|---|
| `python -m compileall -q agent_solution/intake agent_solution` | PASS |
| `python -m pytest agent_solution/tests/test_intake.py -v` | PASS (28/28) |
| `python -m pytest agent_solution/tests/test_git_context.py -v` | PASS (31/31) |
| `python -m ruff check agent_solution/intake agent_solution/tests/test_intake.py agent_solution/tests/test_git_context.py` | PASS |
| `python -m agent_solution --help` | PASS |
| `git diff --check` | PASS |

## Manual Smoke Summary

Against the actual project repository:

```
decision: ACCEPT_WITH_SAFE_DEFAULTS
scope: Current working-tree diff.
context_status: COLLECTED
head_sha: 8e1d1d7269c4
changed_file_count: 25
staged_count: 0
unstaged_count: 2
untracked_count: 7
excerpt_count: 8
excluded_count: 17
fingerprint_complete: False
cache_ineligibility: ['excerpt_file_limit_reached' × 17]
```

The fingerprint is correctly marked incomplete because the repository has more changed files than the excerpt file limit (8).  This is the expected conservative behavior.

## Limitations

1. Binary detection is content-based and may not catch all formats
2. Sensitive detection uses pattern matching, not content inspection
3. Excerpts start at line 1; selective line ranges not yet supported
4. `BOUNDED_REPOSITORY_SEARCH` prepares inventory contract only — no content collection
5. Fingerprint incompletion correctly disables cache reuse for incomplete states

## Explicit Statement

Phase 2 remains pending `Phase-02-REVIEW-02`.  This implementation does not mark Phase 2B or Phase 2 as accepted.  No review artifact was created.
