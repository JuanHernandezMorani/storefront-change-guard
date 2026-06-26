# Prompt Report — Phase 02B: Git Context Collection

## Metadata

| Field | Value |
|---|---|
| Prompt ID | `prompt-006-phase-02B-git-context-collection` |
| Phase | Phase 2B — Git Context Collection and Deterministic Evidence Snapshot |
| Task | Implement deterministic, bounded, model-agnostic Git context collector |
| Date | 2026-06-24 |

## Prompt Summary

The prompt requested implementation of Phase 2B: Git Context Collection, including:

1. Typed data contracts for Git context evidence
2. Deterministic repository fingerprinting for cache invalidation
3. Bounded changed-file discovery with scope modes
4. Safe file excerpt collection with sensitive/binary/oversized handling
5. Read-only Git command execution with provenance tracking
6. Intake integration respecting Phase 2A decisions
7. Comprehensive test suite using temporary Git repositories
8. Technical documentation

## Implementation Approach

### Data contracts (models.py)

Created 12 typed contracts using the project's existing conventions:
- Frozen dataclasses with `slots=True`
- `StrEnum` for enumerations
- Explicit `UTC` datetime usage
- Null/unavailable states rather than invented values

### Git command safety (collector.py)

Implemented `_run_git` helper that:
- Uses `subprocess.run` with `shell=False`
- Passes argument arrays (never string interpolation)
- Records full command provenance (command, exit_code, stdout_length, stderr_length, timed_out, cwd, duration_ms)
- Enforces configurable timeouts
- Bounds output to `max_command_output_bytes`

### Fingerprinting (fingerprint.py)

Implemented deterministic SHA-256 based fingerprinting:
- Hashes actual diff content (not just file paths)
- Marks `is_complete_for_cache=False` when any content is truncated or excluded
- Records explicit `cache_ineligibility_reasons` for cache layer rejection

### Excerpt collection (excerpts.py)

Implemented bounded text extraction:
- UTF-8 decoding with `errors="replace"`
- Per-file and aggregate byte limits
- Sensitive/binary exclusion before text extraction
- SHA-256 of captured text for integrity

### Scope modes

Four scope modes implemented:
- `working_tree_diff`: collect only changed files
- `explicit_paths`: validate and filter to specified paths
- `bounded_repository_search`: prepare inventory contract (no content)
- `no_actionable_scope`: return structured no-op

### Test suite (test_git_context.py)

31 tests using temporary Git repositories:
- Each test creates an isolated repo in `tmp_path`
- Tests never mutate the actual project repository
- Covers all 18 required scenarios plus additional edge cases

## Files Created/Modified

| File | Action | Lines |
|---|---|---|
| `agent_solution/git_tools/__init__.py` | Updated | 6 |
| `agent_solution/git_tools/models.py` | Created | 230 |
| `agent_solution/git_tools/collector.py` | Created | 470 |
| `agent_solution/git_tools/fingerprint.py` | Created | 95 |
| `agent_solution/git_tools/excerpts.py` | Created | 115 |
| `agent_solution/tests/test_git_context.py` | Created | 620 |
| `docs/phase-02-git-context-collection.md` | Created | 195 |
| `REPORT/executions/run-006-phase-02B-validation.md` | Created | 150 |
| `REPORT/prompts/prompt-006-phase-02B-git-context-collection.md` | Created | this file |

## Validation

All validation commands pass:
- compileall: PASS
- Phase 2A intake tests: 28/28 PASS
- Phase 2B git context tests: 31/31 PASS
- ruff: All checks passed
- agent CLI help: PASS
- git diff --check: PASS
- Manual smoke test: PASS (actual repository, read-only)
