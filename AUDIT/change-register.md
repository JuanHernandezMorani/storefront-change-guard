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
| AI-generated defects requiring tracked fixes | 1 |
| AI-assisted defects requiring tracked fixes | 0 |
| Human-authored defects requiring tracked fixes | 0 |
| Upstream baseline defects requiring tracked fixes | 0 |

---

## Change Records

| Identifier | Type | Parent Phase | Originating Phase | Detection Phase | Status | Severity | Origin | Model Involvement | Detection Source | Root Cause Summary | Audit Link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `Phase-01-FIX-01` | Fix | Phase-01 | Phase-01 | Phase-01 | Accepted | Medium | AI-generated | Direct | Manual validation and build | Empty-object identity sentinel always compared false | [phase-01-FIX-01-context-boundary-remediation.md](phase-01-FIX-01-context-boundary-remediation.md) |

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
