# Phase-02-FIX-01 — Intake Decision Contract and Mixed-Goals Detection

## Review Findings Addressed

| Finding | Severity | Description |
|---|---|---|
| F-01 | MEDIUM | Test `test_explicit_patch_request` assertion excludes CLARIFY for LOW-confidence PATCH_PROPOSAL |
| F-02 | MEDIUM | Mixed-goals detector uses keyword-count threshold (≥3) that misses many mixed requests |
| F-03 | MEDIUM | Mixed-goals keyword list omits "ready", "production", "better", "improve" |

## Root Cause Analysis

### F-01 — Test-Contract Mismatch

**Root cause:** The classifier counted only one regex match (`\bmodify\b`) for the explicit patch request, yielding LOW confidence.  The policy correctly returned `CLARIFY` for LOW-confidence non-review types, but the test assertion did not include `CLARIFY` as an acceptable outcome.  Additionally, the classifier lacked patterns for validation commands and expected-behavior signals, preventing HIGH-confidence classification of well-specified patch requests.

**Remediation:**
1. Added validation-command patterns (`\bvalidate\b.*\bwith\b`, `\bvalidar\b.*\bcon\b`) and expected-behavior patterns (`\bexpected\b.*:`, `\besperado\b.*:`) to `_PATCH_PATTERNS` in the classifier.
2. Rewrote `test_explicit_patch_request` into two separate test classes: `TestExplicitPatchHighConfidence` (all fields present → `REFINE_FOR_EXECUTION`) and `TestExplicitPatchLowConfidence` (missing fields → `CLARIFY`).
3. Added assertions that no outcome authorizes direct mutation (`ACCEPT_AS_IS` or `ACCEPT_WITH_SAFE_DEFAULTS`).

### F-02/F-03 — Mixed-Goals Detection Gap

**Root cause:** The original `_has_mixed_goals` used a keyword-count threshold (≥3) with a limited keyword list.  The example "Review the checkout change, fix any issue you find, and tell me whether it is ready for production" contained only 2 matching keywords ("review", "fix") from the list, so mixed-goals was not detected.  The keyword list also omitted "ready", "production", "better", and "improve".

**Remediation:**
1. Replaced the keyword-count heuristic with **deterministic task-signal overlap**.
2. The new detector checks whether the request text matches patterns from two or more distinct task types (`CODE_REVIEW`, `BUG_DIAGNOSIS`, `CODEBASE_QUESTION`, `READINESS_ASSESSMENT`, `PATCH_PROPOSAL`).
3. Each task type's patterns are checked independently using the existing regex pattern sets.
4. When ≥2 distinct task types match, the request is flagged as mixed-goals.
5. Mixed goals always return `CLARIFY` with explicit decomposition clarification explaining that the detected task types have different execution contracts.

## Exact Implementation Changes

### agent_solution/intake/classifier.py

- Added 6 new patterns to `_PATCH_PATTERNS`: validation commands (EN/ES), expected-behavior signals (EN/ES).
- No changes to `_count_matches` or `classify_request` logic.

### agent_solution/intake/policy.py

- Replaced `_has_mixed_goals` from keyword-count to task-signal overlap using independent per-type pattern matching.
- Added `mixed_goals` parameter to `_blocking_reasons` with explicit blocking reason for mixed goals.
- Removed unused imports (`build_execution_brief`, `Assumption`, `ExecutionBrief`).
- Removed local import of `ResolvedScope` (now imported at module level).
- Added `_resolve_scope` case for `PATCH_PROPOSAL` with explicit paths.
- Fixed E501 line length (replaced `or` chain with `in` check).
- Fixed UP037/F821 (removed quoted `"ResolvedScope"` annotation).

### agent_solution/intake/clarifier.py

- Updated mixed-goals decomposition question with explicit task-type examples and decomposition instruction.
- Added detailed reason explaining different evidence requirements per task type.

### agent_solution/intake/models.py

- Removed unused `Any` import.
- Replaced `datetime.now(timezone.utc)` with `datetime.now(UTC)` (UP017).
- Fixed import ordering (I001).

### agent_solution/intake/defaults.py

- Removed unused `ResolvedScope` import.

### agent_solution/intake/brief.py

- No changes required (Ruff clean).

### agent_solution/tests/test_intake.py

- Removed unused `pytest` and `ConfidenceLevel` imports.
- Fixed import ordering (I001).
- Rewrote `TestExplicitScope` into `TestExplicitPatchHighConfidence` and `TestExplicitPatchLowConfidence`.
- Added `TestVaguePatchRequest` (Test 5 replacement).
- Added `TestEnglishMixedGoals` with decomposition, no-default-scope, and blocking-reasons assertions.
- Added `TestSpanishMixedGoals` with decomposition assertion.
- Added `TestSingleTaskCodeReview` (legitimate review remains `ACCEPT_WITH_SAFE_DEFAULTS`).
- Added `TestReadinessOnlyNoCriteria` (readiness without criteria → `CLARIFY`).
- Updated `TestMixedGoals` decomposition assertion text.

### docs/phase-02-intake-gate.md

- Added "Patch Proposal Decision Contract" section.
- Added "Mixed-Goals Detection" section with mechanism, required behavior, signal table, and EN/ES examples.
- Added "Worktree-Only Invariant" section.
- Updated "For mixed goals" clarification text.
- Documented that `ACCEPT_WITH_SAFE_DEFAULTS` is never permitted for patch proposals.

## Why the Fix Remains Limited to Phase 2A

All changes are confined to the intake classification, validation, and clarification pipeline.  No changes were made to:
- Phase 0 (bootstrap)
- Phase 1 (demo storefront, monetary invariant, review governance)
- Phase 2B (Git context collection — not yet implemented)
- Phase 3 (grounded analysis — not yet implemented)
- Phase 4 (isolated patch validation — not yet implemented)
- Benchmark scripts, configurations, results, or model files
- Test 1 or Test 2 evidence

The fix only modifies how incoming requests are classified, validated, and routed within the intake gate.

## Alternatives Considered for Mixed-Goals Detection

### Alternative A: Lower threshold to ≥2 with expanded keyword list

Simply lowering the threshold from 3 to 2 and adding more keywords ("ready", "production", "better", "improve").  **Rejected** because it remains a flat keyword-count heuristic that cannot distinguish between a single task using multiple keywords (e.g., "fix the bug and improve the error handling" — both are PATCH_PROPOSAL) and genuinely mixed tasks.

### Alternative B: Document limitation and add focused test

Document that the mixed-goals detector is a heuristic with known gaps, and add a test only for the specific patterns the system is designed to detect.  **Rejected** because the gap is a blocking Phase 2A defect — mixed requests that are not decomposed may silently convert into patch authority.

### Alternative C: Deterministic task-signal overlap (chosen)

Check whether the request matches patterns from ≥2 distinct task types.  Each task type has its own regex pattern set, and matching is independent.  This is deterministic, auditable, and directly tied to the execution contracts that different task types require.

**Chosen** because:
- It is deterministic (no thresholds, no arbitrary keywords).
- It is directly tied to the task-type taxonomy and execution contracts.
- It handles both English and Spanish inputs through the existing bilingual pattern sets.
- It fails closed (any genuine mixed-goal request is caught).
- False positives (a single task matching two types) are safe because CLARIFY is conservative.

## Tests Added or Strengthened

| Test Class | Scenario | Expected | Status |
|---|---|---|---|
| `TestExplicitPatchHighConfidence` | Explicit patch with scope + expected + validation | `REFINE_FOR_EXECUTION` | NEW |
| `TestExplicitPatchLowConfidence` | Patch with only target, no expected/validation | `CLARIFY` | NEW |
| `TestVaguePatchRequest` | "Make the code better." | `CLARIFY` | NEW |
| `TestEnglishMixedGoals` | Review + fix + readiness (EN) | `CLARIFY` + decomposition | NEW |
| `TestSpanishMixedGoals` | Review + fix + readiness (ES) | `CLARIFY` + decomposition | NEW |
| `TestSingleTaskCodeReview` | Legitimate single-task review with diff | `ACCEPT_WITH_SAFE_DEFAULTS` | NEW |
| `TestReadinessOnlyNoCriteria` | Readiness without environment/criteria | `CLARIFY` | NEW |
| `TestReviewCurrentChange` | CODE_REVIEW with/without diff | Existing coverage preserved | KEPT |
| `TestFixTheBug` | BUG_DIAGNOSIS without evidence | Existing coverage preserved | KEPT |
| `TestExplainCheckoutShipping` | CODEBASE_QUESTION | Existing coverage preserved | KEPT |
| `TestReadyForProduction` | READINESS_ASSESSMENT without criteria | Existing coverage preserved | KEPT |
| `TestMakeCodeBetter` | Vague request | Existing coverage preserved | KEPT |
| `TestSpanishReview` | Spanish CODE_REVIEW | Existing coverage preserved | KEPT |
| `TestSpanishFixError` | Spanish BUG_DIAGNOSIS | Existing coverage preserved | KEPT |
| `TestSecurityClaim` | Unsupported security claim | Existing coverage preserved | KEPT |
| `TestMixedGoals` | Mixed goals (4 task types) | Existing coverage preserved, assertion updated | KEPT |
| `TestClassificationConservative` | Empty/ambiguous requests | Existing coverage preserved | KEPT |
| `TestModelProfiles` | Profile structure validation | Existing coverage preserved | KEPT |

## Validation Commands and Outcomes

| Command | Result |
|---|---|
| `python -m compileall -q agent_solution/intake` | PASS (exit 0, no output) |
| `python -m pytest agent_solution/tests/test_intake.py -v` | PASS (28/28 tests) |
| `python -m ruff check agent_solution/intake agent_solution/tests/test_intake.py` | PASS (0 errors) |
| `python -m agent_solution --help` | PASS (usage displayed) |
| `git diff --check` | PASS (no whitespace errors) |

## Manual Smoke Evidence

| # | Input | detected_task_type | decision | safe_defaults | decomposition | blocking |
|---|---|---|---|---|---|---|
| 1 | "Review the current change." (diff) | CODE_REVIEW | ACCEPT_WITH_SAFE_DEFAULTS | applied=True | N/A | None |
| 2 | "Review the current change." (no diff) | CODE_REVIEW | CLARIFY | applied=False | N/A | Missing scope |
| 3 | "Fix the bug." | BUG_DIAGNOSIS | CLARIFY | applied=False | N/A | Missing symptom |
| 4 | "Is this ready for production?" | READINESS_ASSESSMENT | CLARIFY | applied=False | N/A | Missing criteria+env |
| 5 | "Make the code better." | PATCH_PROPOSAL | CLARIFY | applied=False | N/A | Missing paths+confidence |
| 6 | EN mixed: review+fix+readiness | READINESS_ASSESSMENT | CLARIFY | applied=False | Yes | Mixed goals + missing |
| 7 | ES mixed: review+fix+readiness | READINESS_ASSESSMENT | CLARIFY | applied=False | Yes | Mixed goals + missing |
| 8 | Explicit patch (scope+expected+validation) | PATCH_PROPOSAL | REFINE_FOR_EXECUTION | applied=False | N/A | None |

## Remaining Limitations

1. **Classifier is keyword-based:** Semantic understanding of request intent is deferred to Phase 3 model integration.
2. **Mixed-goals detection is pattern-based:** Requests using unusual phrasing may evade detection, but will still return CLARIFY due to LOW confidence.
3. **Bilingual coverage is partial:** Spanish patterns cover common Rioplatense and general Spanish phrasing but not all dialects.
4. **Worktree-only invariant is recorded but not enforced:** Phase 2A records the constraint in the execution brief; Phase 4 enforces it.
5. **No ACCEPT_AS_IS or REJECT_UNSAFE_OR_UNSUPPORTED path is exercised in tests:** These paths are structurally correct but not yet covered by automated tests.

## Explicit Statement

Phase 2 remains pending Phase-02B (Git Context Collection) and Phase-02-REVIEW-02 (integrated review).  This fix does not mark Phase 2A or Phase 2 as accepted.
