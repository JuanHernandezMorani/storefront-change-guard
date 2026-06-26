# Change Register

Consolidated register of fixes and enhancements across all phases.

---

## Summary Metrics

| Metric | Value |
|---|---|
| Completed implementation phases | 1 |
| Open fixes | 0 |
| Accepted fixes | 1 |
| Open enhancements | 0 |
| Accepted enhancements | 0 |
| Validations completed | 1 |
| AI-generated defects requiring tracked fixes | 1 |
| AI-assisted defects requiring tracked fixes | 0 |
| Human-authored defects requiring tracked fixes | 0 |
| Upstream baseline defects requiring tracked fixes | 0 |

---

## Change Records

| Identifier | Type | Parent Phase | Originating Phase | Detection Phase | Status | Severity | Origin | Model Involvement | Detection Source | Root Cause Summary | Audit Link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `Phase-01-FIX-01` | Fix | Phase-01 | Phase-01 | Phase-01 | Accepted | Medium | AI-generated | Direct | Manual validation and build | Empty-object identity sentinel always compared false | [phase-01-FIX-01-context-boundary-remediation.md](phase-01-FIX-01-context-boundary-remediation.md) |
| `Phase-03-VALIDATION-02` | Validation | Phase-03 | Phase-03 | Phase-03 | Completed | N/A | AI-assisted | Direct | Live smoke test execution | Phase-03-FIX-01 runtime correction validated | [phase-03-validation-02-corrected-live-runtime.md](phase-03-validation-02-corrected-live-runtime.md) |

---

## Phase Quality Summary

| Phase | New Implementations | Fixes Required | Fixes Accepted | Enhancements | Open Blocking Items | Acceptance |
|---|---:|---:|---:|---:|---:|---|
| Phase-00 | 1 | 0 | 0 | 0 | 0 | Accepted |
| Phase-01 | 1 | 1 | 1 | 0 | 0 | Accepted |

---

## Phase-01-FIX-02 Implementation Record — 2026-06-23

### Identifier

`Phase-01-FIX-02`

### Type

Fix

### Parent Phase

`Phase-01`

### Status

Implementation complete — pending Phase-01-REVIEW-02

### Scope

Monetary integer-cent validation and review-governance normalization.

### Root Cause Summary

The prior monetary contract documented integer cents but did not reject fractional cent values at runtime. `calculateShipping()` and `toDisplay()` accepted values such as `5000.5`, violating the documented domain invariant.

### Validation Summary

- `npm ci` — passed (248 packages installed; 13 upstream vulnerabilities reported, out of scope)
- `npm run lint` — passed (0 errors, 0 warnings)
- `npm run build` — passed (371 modules transformed; no TypeScript, Vite, or esbuild warnings)
- `npm test` — passed (3 test files, 23 tests: 6 shipping + 16 money + 1 useShoppingCart)
- `git diff --check` — passed (no whitespace errors; Windows CRLF line-ending warnings only)

### Audit Link

[phase-01-FIX-02-monetary-invariant-and-review-governance.md](phase-01-FIX-02-monetary-invariant-and-review-governance.md)

---

## Current Status Snapshot — 2026-06-23

This snapshot reflects the project state after `Phase-01-FIX-02` implementation and before `Phase-01-REVIEW-02`. Earlier summary metrics and tables remain preserved as historical records.

| Metric | Current Value |
|---|---:|
| Open fixes | 1 |
| Accepted fixes | 1 |
| Open enhancements | 0 |
| Accepted enhancements | 0 |
| AI-generated defects requiring tracked fixes | 1 |
| Human-authored defects requiring tracked fixes | 1 |
| Upstream baseline defects requiring tracked fixes | 0 |

| Work Item | Current State |
|---|---|
| Phase-00 | Accepted |
| Phase-01 | Pending `Phase-01-REVIEW-02` |
| Phase-01-FIX-01 | Accepted |
| Phase-01-FIX-02 | Implementation complete — pending `Phase-01-REVIEW-02` |

---

## Phase-01-REVIEW-02 Review Outcome — 2026-06-23

### Identifier

`Phase-01-REVIEW-02`

### Reviewed Work

- `Phase-01` (demo storefront preparation)
- `Phase-01-FIX-01` (context provider boundary remediation)
- `Phase-01-FIX-02` (monetary invariant and review governance)

### Reviewed Commit

`a5fe91c89c230b636280c204dc320729450f3a6d`

### Outcome

`CHANGES_REQUIRED`

### Blocking Finding Count

1

### Brief Rationale

Commit-level whitespace error detected in `demo-storefront/docs/checkout-rules-addendum-01-monetary-invariant.md` (lines 3 and 4 contain trailing whitespace). All functional validation passed (lint, build, 23 tests), but the whitespace defect violates mandatory quality gates.

### Next Action

`Phase-01-FIX-03` to correct trailing whitespace in `checkout-rules-addendum-01-monetary-invariant.md`, followed by `Phase-01-REVIEW-03` for re-evaluation.

### Audit Link

[phase-01-REVIEW-02-final-phase-01-acceptance.md](phase-01-REVIEW-02-final-phase-01-acceptance.md)

---

## Phase-02-FIX-01 Implementation Record — 2026-06-24

### Identifier

`Phase-02-FIX-01`

### Type

Fix

### Parent Phase

`Phase-02A`

### Status

Implementation complete — pending Phase-02-REVIEW-02

### Scope

Intake decision contract for patch proposals and deterministic mixed-goals detection.

### Originating Finding

- F-01 (MEDIUM): Test `test_explicit_patch_request` assertion excluded CLARIFY for LOW-confidence PATCH_PROPOSAL.
- F-02 (MEDIUM): Mixed-goals detector used keyword-count threshold (≥3) that missed many mixed requests.
- F-03 (MEDIUM): Mixed-goals keyword list omitted readiness and improvement signals.

### Root Cause Summary

The classifier lacked patterns for validation commands and expected-behability signals, preventing HIGH-confidence classification of well-specified patch requests.  The mixed-goals detector used a flat keyword-count heuristic that could not distinguish between a single task using multiple keywords and genuinely mixed tasks requiring decomposition.

### Remediation Summary

1. Added validation-command and expected-behavior patterns to `_PATCH_PATTERNS`.
2. Replaced keyword-count mixed-goals heuristic with deterministic task-signal overlap.
3. Rewrote test-008 into high-confidence and low-confidence variants.
4. Added 7 new test classes covering all required scenarios.
5. Fixed all 17 Ruff warnings across scoped files.
6. Updated documentation with patch proposal decision contract, mixed-goals detection mechanism, and worktree-only invariant.

### Validation Summary

- `python -m compileall -q agent_solution/intake` — PASS
- `python -m pytest agent_solution/tests/test_intake.py -v` — PASS (28/28)
- `python -m ruff check agent_solution/intake agent_solution/tests/test_intake.py` — PASS (0 errors)
- `python -m agent_solution --help` — PASS
- `git diff --check` — PASS
- 8/8 manual smoke cases PASS

### Audit Link

[phase-02-FIX-01-intake-decision-contract-and-mixed-goals.md](phase-02-FIX-01-intake-decision-contract-and-mixed-goals.md)

---

## Phase-02B Implementation Record — 2026-06-24

### Identifier

`Phase-02B`

### Type

Implementation

### Parent Phase

`Phase-02`

### Status

Implementation complete — pending Phase-02-REVIEW-02

### Scope

Git Context Collection, Deterministic Evidence Snapshot, Repository Fingerprinting, Bounded Changed-File Discovery, Safe Excerpt Collection, Evidence Manifest Generation.

### Implementation Summary

1. Created 12 typed data contracts (frozen dataclasses) for Git context evidence.
2. Implemented deterministic repository fingerprinting with SHA-256 hashing for cache invalidation.
3. Implemented bounded changed-file discovery with 4 scope modes.
4. Implemented safe file excerpt collection with sensitive/binary/oversized handling.
5. Implemented read-only Git command execution with argument arrays, timeouts, and provenance tracking.
6. Implemented intake integration respecting Phase 2A decisions.
7. Created 31 test cases using temporary Git repositories (all passing).
8. Created technical documentation.

### Validation Summary

- `python -m compileall -q agent_solution/intake agent_solution` — PASS
- `python -m pytest agent_solution/tests/test_intake.py -v` — PASS (28/28)
- `python -m pytest agent_solution/tests/test_git_context.py -v` — PASS (31/31)
- `python -m ruff check agent_solution/intake agent_solution/tests/test_intake.py agent_solution/tests/test_git_context.py` — PASS
- `python -m agent_solution --help` — PASS
- `git diff --check` — PASS
- Manual smoke test against actual repository — PASS

### Audit Link

[phase-02B-git-context-collection.md](phase-02B-git-context-collection.md)

---

## Phase-03 Implementation Record — 2026-06-24

### Identifier

`Phase-03`

### Type

Implementation

### Parent Phase

`Phase-03`

### Status

Implementation complete — pending Phase-03 independent review

### Scope

Evidence-Grounded Semantic Analysis with One Local Model

### Implementation Summary

1. Created 18 typed data contracts (frozen dataclasses) for analysis models.
2. Implemented LocalModelRunner using llama.cpp CLI with subprocess (shell=False).
3. Implemented EvidenceBundleBuilder consuming Phase 2 intake and Git context.
4. Implemented deterministic evidence-expansion pass within Phase 2 scope.
5. Implemented OutputValidator for model JSON output with claim policy enforcement.
6. Implemented ResultRenderer for structured output with language support (EN/ES).
7. Implemented SQLite-backed AnalysisCache with deterministic keys.
8. Implemented SQLite-backed SessionStateStore with compact structured state.
9. Implemented AnalysisOrchestrator coordinating full pipeline.
10. Added analyze subcommand to CLI with all required options.
11. Created 60 test cases (47 grounded analysis + 13 local model runner), all passing.
12. Single-model configuration only - no fallback, no routing, no cloud APIs.
13. Anti-loop limits enforced (max_model_invocations_per_request = 1).

### Validation Summary

- `python -m compileall -q agent_solution` — PASS
- `python -m pytest agent_solution/tests/test_intake.py -v` — PASS (28/28)
- `python -m pytest agent_solution/tests/test_git_context.py -v` — PASS (31/31)
- `python -m pytest agent_solution/tests/test_grounded_analysis.py -v` — PASS (47/47)
- `python -m pytest agent_solution/tests/test_local_model_runner.py -v` — PASS (13/13)
- `python -m ruff check agent_solution` — PASS
- `python -m agent_solution --help` — PASS
- `python -m agent_solution analyze --help` — PASS
- `git diff --check` — PASS
- `git diff --cached --check` — PASS
- `git check-ignore -v agent_solution/model/Qwen3.5-4B-UD-Q4_K_XL.gguf` — PASS

### Audit Link

[phase-03-grounded-analysis-single-local-model.md](phase-03-grounded-analysis-single-local-model.md)

---

## Phase-03 Validation 01 — Live Single-Model Runtime Validation Record — 2026-06-24

### Identifier

`Phase-03-VALIDATION-01`

### Type

Validation Record (non-implementation)

### Parent Phase

`Phase-03`

### Status

`CHANGES_REQUIRED`

### Scope

Live smoke validation of Phase 3 CLI integration with the selected single model (`Qwen3.5-4B-UD-Q4_K_XL.gguf`) through the real local model runner.

### Outcome Summary

Phase 3 unit tests pass (119/119 across all test suites). All final validation commands pass. However, live model smoke tests (Smoke 1, 2, 3) cannot complete because the `LocalModelRunner` uses `llama-cli` which enters interactive conversation mode for models with chat templates, preventing single-turn completion.

### Blocking Finding

The `LocalModelRunner` (`agent_solution/model/runner.py`) uses `llama-cli` which cannot operate in non-interactive completion mode for the Qwen3.5-4B model. When `llama-cli` detects a chat template, it automatically enters interactive conversation mode. The `-no-cnv` flag is not supported by `llama-cli`, and `-st` / `--single-turn` does not prevent interactive mode. The correct executable for non-interactive single-turn completion is `llama-completion`.

### Validated Items (Unit Test Level)

- Model unavailable failure path (MODEL_UNAVAILABLE status)
- Invalid output defensive path (MODEL_OUTPUT_INVALID status)
- Prompt injection resistance (evidence treated as data only)
- No retry after failure
- No fallback model attempted
- No cache success entry on failure
- All 12 final validation commands pass

### Audit Link

[phase-03-validation-01-live-single-model-runtime.md](phase-03-validation-01-live-single-model-runtime.md)

### Execution Report

[run-009-phase-03-validation-01-live-runtime.md](../REPORT/executions/run-009-phase-03-validation-01-live-runtime.md)

---

## Phase-03-FIX-01 Implementation Record — 2026-06-24

### Identifier

`Phase-03-FIX-01`

### Type

Fix

### Parent Phase

`Phase-03`

### Status

Implementation complete — pending Phase-03 live validation

### Scope

Non-Interactive Local Completion Runtime.

### Originating Finding

- F-01 (HIGH): `LocalModelRunner` uses `llama-cli` which enters interactive conversation mode for models with chat templates, preventing single-turn completion.

### Root Cause Summary

The `LocalModelRunner` invokes `llama-cli`. For the selected Qwen model with a chat template, the installed `llama-cli` enters interactive conversation mode under the current invocation pattern. The `-no-cnv` flag is not supported by the installed `llama-cli` executable, and `-st` does not reliably prevent interactive conversation mode when used with `-p`.

### Remediation Summary

1. Replaced `llama-cli` with `llama-completion` as the configured single-turn local completion executable.
2. Added `-no-cnv` flag for non-interactive completion mode.
3. Implemented safe prompt transport using temporary files (`-f` flag) instead of `-p` argument.
4. Migrated configuration from `STORE_FRONT_GUARD_LLAMA_CLI` to `STORE_FRONT_GUARD_LLAMA_EXECUTABLE`.
5. Removed hardcoded path auto-discovery; user must provide explicit executable path.
6. Updated `SingleModelRuntimeConfig` dataclass with generic executable fields.
7. Improved timeout and process-cleanup behavior for Windows.
8. Updated 19 test cases in `test_local_model_runner.py` for new configuration.
9. Updated 4 test cases in `test_grounded_analysis.py` for new configuration.

### Validation Summary

- `python -m compileall -q agent_solution` — PASS
- `python -m pytest agent_solution/tests/test_intake.py -v` — PASS (28/28)
- `python -m pytest agent_solution/tests/test_git_context.py -v` — PASS (31/31)
- `python -m pytest agent_solution/tests/test_grounded_analysis.py -v` — PASS (47/47)
- `python -m pytest agent_solution/tests/test_local_model_runner.py -v` — PASS (19/19)
- `python -m ruff check agent_solution` — PASS
- `python -m agent_solution --help` — PASS
- `python -m agent_solution analyze --help` — PASS
- `git diff --check` — PASS
- `git diff --cached --check` — PASS
- `git check-ignore -v agent_solution/model/Qwen3.5-4B-UD-Q4_K_XL.gguf` — PASS

### Audit Link

[phase-03-FIX-01-non-interactive-local-completion-runtime.md](phase-03-FIX-01-non-interactive-local-completion-runtime.md)

### Execution Report

[run-010-phase-03-FIX-01-validation.md](../REPORT/executions/run-010-phase-03-FIX-01-validation.md)

---

## Phase-03-VALIDATION-02 Validation Record — 2026-06-25

### Identifier

`Phase-03-VALIDATION-02`

### Type

Validation

### Parent Phase

Phase-03

### Originating Phase

Phase-03

### Detection Phase

Phase-03

### Status

Completed

### Severity

N/A (Validation)

### Origin

AI-assisted

### Detection Source

Live smoke test execution

### Root Cause Summary

Phase-03-FIX-01 changed the local runtime adapter from `llama-cli` to `llama-completion` because the selected Qwen model entered interactive conversation mode under the prior `llama-cli` invocation. The Phase-03-FIX-01 deterministic tests passed, but its real local-model smoke tests were not executed. This validation completed those live tests.

### Validation Results

| Test | Status | Notes |
|---|---|---|
| Smoke A: English code review | PASS | Runtime executed correctly |
| Smoke B: Cache hit | PASS | Cache behavior correct |
| Smoke C: Spanish question | PASS | Intake and evidence correct |
| Smoke D: Prompt injection | PASS | Injection resisted |
| Model unavailable | PASS | MODEL_UNAVAILABLE returned |
| Timeout | PASS | MODEL_TIMEOUT returned |
| Invalid output | PASS | MODEL_OUTPUT_INVALID returned |
| Deterministic validation | PASS | All 11 commands pass |
| Project integrity | PASS | No unauthorized modifications |

### Final Classification

**VALIDATED**

### Phase-03-FIX-01 Runtime Resolution Status

The Phase-03-FIX-01 runtime correction is now **confirmed**. The change from `llama-cli` to `llama-completion` resolves the interactive conversation mode issue.

### Audit Link

[phase-03-validation-02-corrected-live-runtime.md](phase-03-validation-02-corrected-live-runtime.md)

### Execution Report

[run-012-phase-03-validation-02-live-runtime.md](../REPORT/executions/run-012-phase-03-validation-02-live-runtime.md)

---

## Phase-03-FIX-02 Implementation Record — 2026-06-25

### Identifier

`Phase-03-FIX-02`

### Type

Fix

### Parent Phase

`Phase-03`

### Status

Implementation complete — deterministic tests pass (182/182), live smoke tests pending

### Scope

Test 1 Runtime Reconciliation, Structured Output Reliability, Bounded Codebase Q&A, Explicit File Target Evidence Collection

### Root Cause Summary

Phase-03-FIX-01 selected `llama-completion` as the production executable because `llama-cli` appeared to lack non-interactive support. However, Test 1 benchmark evidence showed that `llama-cli` with `--jinja`, `-st`, `-f`, and `--no-display-prompt` successfully produced JSON output. The `-no-cnv` flag shown in `llama-cli --help` is a documentation artifact — it is not actually supported at runtime.

Qwen3.5 emits `<think>`/`</think>` reasoning blocks regardless of runtime flags. Phase-03-FIX-01 had no envelope parser to handle this behavior, causing structured output validation failures.

The bounded repository search in Phase 2 only scanned changed files from git context, producing zero evidence when there were no working-tree changes.

Evidence pipeline ignored explicit file targets when no git diffs existed, causing empty evidence bundle (SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`).

### Implementation Summary

1. **Runtime reconciliation**: Selected `llama-cli` as the single production executable, reconciled with Test 1 profile (`--jinja`, `-st`, `-f`, `--no-display-prompt`, stdin=DEVNULL).
2. **Reasoning envelope parser**: Added `extract_reasoning_envelope()` supporting Shape A (plain JSON) and Shape B (`<think>`/`</think>` envelope). Reasoning discarded immediately after extraction.
3. **Context budget**: Added reasoning reservation (512 tokens) and final JSON reservation (max(512, completion_limit)). Updated to use `completion_limit` and `reserved_generation_margin` directly.
4. **Bounded evidence**: Updated `EvidenceBundleBuilder` to scan entire repository for `CODEBASE_QUESTION` (not just changed files).
5. **Explicit file targets**: Added `explicit_file_targets` to `ResolvedScope` and `extract_file_targets` to classifier. Updated evidence builder to include explicit file target evidence for `CODE_REVIEW` and `BUG_DIAGNOSIS`.
6. **Empty evidence check**: Updated orchestrator to check for empty evidence records and enforce context budget invariant.
7. **System prompt**: Strengthened to require JSON after optional `<think>` block.

### Validation Results

| Test | Status | Notes |
|---|---|---|
| `test_intake.py` | PASS | 28/28 passed |
| `test_git_context.py` | PASS | 31/31 passed |
| `test_grounded_analysis.py` | PASS | 61/61 passed (47 original + 14 new Phase-03-FIX-02 tests) |
| `test_local_model_runner.py` | PASS | 23/23 passed |
| `ruff check agent_solution` | PASS | All checks passed |
| `python -m agent_solution --help` | PASS | Help output displayed |
| `python -m agent_solution analyze --help` | PASS | Help output displayed |
| `git diff --check` | PASS | No whitespace errors |
| `git diff --cached --check` | PASS | No whitespace errors |
| `git check-ignore -v agent_solution/model/*.gguf` | PASS | GGUF files ignored |
| Live smoke tests (A-G) | PENDING | Require actual model execution |

### Final Classification

**DETERMINISTIC VALIDATION PASSED — Live smoke tests pending**

### Audit Link

[phase-03-FIX-02-reference-runtime-and-structured-output.md](phase-03-FIX-02-reference-runtime-and-structured-output.md)

### Execution Report

[run-013-phase-03-FIX-02-validation.md](../REPORT/executions/run-013-phase-03-FIX-02-validation.md)

### Prompt Record

[prompt-013-phase-03-FIX-02-reference-runtime-and-structured-output.md](../REPORT/prompts/prompt-013-phase-03-FIX-02-reference-runtime-and-structured-output.md)

| Phase-02-FIX-02 | Fix | Phase-02 | Phase-02 | Phase-02 | In Review | Medium | Human-authored | None | Manual validation and test | Intake classifier lacked defect-discovery and codebase-question patterns; policy rejected bounded file reviews without diff | This session |
| Phase-02-FIX-02 (post-review) | Fix | Phase-02 | Phase-02 | Phase-02 | In Review | Low | Human-authored | None | Manual validation and test | Spanish review regex contained Portuguese-oriented alternatives; missing "do not apply" constraint allowed false PATCH_PROPOSAL signal | This session |

---

## Phase-02-FIX-02 (post-review) Implementation Record — 2026-06-25

### Identifier

`Phase-02-FIX-02 (post-review)`

### Type

Fix (post-review correction)

### Parent Phase

`Phase-02`

### Status

Implementation complete — pending fresh independent review

### Scope

Narrow Spanish review pattern and negative patch constraint.

### Originating Finding

- F-01 (LOW): Spanish review regex contained Portuguese-oriented alternatives (`uma`, `õ`, `ã`) that broadened scope beyond intended Spanish-only behavior.
- F-02 (LOW): Missing constraint pattern for "do not apply" allowed "Do not apply a patch." to trigger PATCH_PROPOSAL signal.

### Root Cause Summary

The Phase-02-FIX-02 Spanish review pattern `hac[ée] (una|uma) revis[io]?[áaóõã]?n?` included Portuguese alternatives not part of the original Spanish-only design. The constraint-phrase list in policy.py lacked "do not apply" / "don't apply" entries, allowing bounded-review requests with negative patch constraints to be misclassified.

### Remediation Summary

1. Replaced Spanish review regex with narrow Spanish-only pattern: `hac[ée] una revis[io]?[áaó]?n?`.
2. Added `\bdo not apply\b` and `\bdon't apply\b` to `_CONSTRAINT_PATTERNS` in policy.py.
3. Added 4 regression tests covering negative patch constraint, affirmative patch retention, and Portuguese rejection.
4. Updated CHANGELOG.md Phase-02-FIX-02 entry to remove "uma/unha" references.

### Validation Summary

- `python -m compileall -q agent_solution` — PASS
- `python -m pytest agent_solution/tests/test_intake.py -v` — PASS
- `python -m ruff check agent_solution` — PASS
- `git diff --check` — PASS
- `git diff --cached --check` — PASS

### Audit Link

[phase-02-FIX-02-post-review-correction.md](phase-02-FIX-02-post-review-correction.md)

---

## Phase-03-FIX-03 Implementation Record — 2026-06-26

### Identifier

`Phase-03-FIX-03`

### Type

Runtime-boundary correction

### Status

Implementation complete — deterministic tests pass; fresh live Gate A pending

### Scope

Sanitize only known `llama-cli` stdout wrapper noise before strict Phase 03
envelope parsing. The parser contract remains strict and is not converted into
an arbitrary JSON searcher.

### Validation

- banner/prompt/trailer sanitization tests
- observed thinking-tag normalization tests
- arbitrary-prose rejection tests
- incomplete/repeated tag rejection tests

---

## Phase 04 Implementation Record — 2026-06-26

### Status

Implementation complete — deterministic worktree tests pass; controlled live
patch validation pending

### Scope

Detached worktree-only patch application, path safety, fixed validation
allowlists, and machine-readable validation artifacts.

---

## Phase 05 Implementation Record — 2026-06-26

### Status

Implementation complete — deterministic policy tests pass; real-artifact
readiness run pending

### Scope

Policy-driven `READY` / `NOT_READY` / `INSUFFICIENT_EVIDENCE` decisions from
Phase 03 and Phase 04 JSON artifacts only.
