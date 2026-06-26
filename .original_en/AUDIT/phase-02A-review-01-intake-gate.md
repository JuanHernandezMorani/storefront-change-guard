# Phase 2A — Request Intake and Prompt Quality Gate: Acceptance Review

## Review Scope

Independent acceptance review of Phase 2A: Request Intake and Prompt Quality Gate foundation. This review validates the intake classification pipeline, decision matrix, safe-default application, clarification generation, model-profile placeholders, test coverage, and documentation correctness.

## Repository Revision

- **Git SHA:** `8e1d1d7269c4ccceaae94fddaf046e67a0e20188`
- **Branch:** main
- **Date:** 2026-06-24

## Files Inspected

| File | Status |
|---|---|
| `agent_solution/intake/__init__.py` | ✅ Present, correct |
| `agent_solution/intake/models.py` | ✅ Present, correct |
| `agent_solution/intake/classifier.py` | ✅ Present, correct |
| `agent_solution/intake/policy.py` | ✅ Present, correct |
| `agent_solution/intake/defaults.py` | ✅ Present, correct |
| `agent_solution/intake/clarifier.py` | ✅ Present, correct |
| `agent_solution/intake/brief.py` | ✅ Present, correct |
| `agent_solution/intake/model_profile.py` | ✅ Present, correct |
| `agent_solution/tests/test_intake.py` | ⚠️ 1 test fails |
| `docs/phase-02-intake-gate.md` | ✅ Present, correct |
| `pyproject.toml` | ✅ Present, correct |

## Validation Commands

### 1. `python -m compileall -q agent_solution/intake`

**Result:** PASS (exit code 0, no output)

### 2. `python -m pytest agent_solution/tests/test_intake.py -v`

**Result:** FAIL (exit code 1)

```
17 collected, 16 passed, 1 failed

FAILED agent_solution/tests/test_intake.py::TestExplicitScope::test_explicit_patch_request
  AssertionError: assert <IntakeDecision.CLARIFY> in (ACCEPT_AS_IS, REFINE_FOR_EXECUTION, ACCEPT_WITH_SAFE_DEFAULTS)
```

The classifier detects `PATCH_PROPOSAL` with `LOW` confidence (only `\bmodify\b` matches; "code", "improve", "better", "refactor" are absent). The policy correctly returns `CLARIFY` for LOW confidence. The test assertion does not include `CLARIFY` as an acceptable outcome.

### 3. `ruff check agent_solution/intake agent_solution/tests/test_intake.py`

**Result:** 17 lint warnings (15 auto-fixable)

| Category | Count | Files |
|---|---|---|
| F401 (unused imports) | 5 | `defaults.py`, `models.py`, `policy.py` ×2, `test_intake.py` |
| I001 (import ordering) | 5 | `models.py`, `policy.py`, `test_intake.py` ×3 |
| E501 (line too long) | 1 | `policy.py:288` |
| UP017 (datetime.UTC alias) | 1 | `models.py:148` |
| UP037 (quoted annotation) | 1 | `policy.py:422` |
| F821 (undefined name) | 1 | `policy.py:422` |

None are correctness issues. All are style/import hygiene.

### 4. `python -m agent_solution --help`

**Result:** PASS

```
usage: storefront-guard [-h] [--version] {status} ...
```

## Manual Smoke-Case Results

| # | Input | Expected Decision | Actual Decision | Pass |
|---|---|---|---|---|
| 1 | "Review the current change." (diff) | `ACCEPT_WITH_SAFE_DEFAULTS` | `ACCEPT_WITH_SAFE_DEFAULTS` | ✅ |
| 2 | "Review the current change." (no diff) | `CLARIFY` | `CLARIFY` | ✅ |
| 3 | "Fix the bug." | `CLARIFY` | `CLARIFY` | ✅ |
| 4 | "Arreglá el error." | `CLARIFY` | `CLARIFY` | ✅ |
| 5 | "Explain how checkout shipping is calculated." | `ACCEPT_WITH_SAFE_DEFAULTS` | `ACCEPT_WITH_SAFE_DEFAULTS` | ✅ |
| 6 | "Is this ready for production?" | `CLARIFY` | `CLARIFY` | ✅ |
| 7 | "Make the code better." | `CLARIFY` | `CLARIFY` | ✅ |
| 8 | "Revisá el cambio actual y decime si rompe el cálculo de envío." (diff) | `ACCEPT_WITH_SAFE_DEFAULTS` | `ACCEPT_WITH_SAFE_DEFAULTS` | ✅ |
| 9 | Explicit patch (file + expected + validation) | `REFINE_FOR_EXECUTION` or `CLARIFY` | `CLARIFY` | ✅* |
| 10 | Mixed: review + fix + readiness | `CLARIFY` with decomposition | `CLARIFY` (no decomposition) | ⚠️ |

*Case 9: CLARIFY is correct per policy (LOW confidence). The test `test-008` incorrectly excludes CLARIFY.

Case 10: Returns CLARIFY (correct) but the decomposition question is not generated because the mixed-goals detector requires ≥3 keyword matches and the request contains only 2 ("review", "fix").

## Decision-Matrix Verification

| Rule | Code Behavior | Docs | Tests | Status |
|---|---|---|---|---|
| UNKNOWN → CLARIFY | ✅ Correct | ✅ Correct | ✅ test-class-01, test-class-02 | PASS |
| LOW confidence → CLARIFY | ✅ Correct | ✅ Correct | ❌ test-008 excludes CLARIFY | FAIL |
| Mixed goals → CLARIFY + decomposition | ✅ Correct | ✅ Correct | ✅ test-010 | PASS (partial) |
| CODE_REVIEW + diff → ACCEPT_WITH_SAFE_DEFAULTS | ✅ Correct | ✅ Correct | ✅ test-001a | PASS |
| CODE_REVIEW no diff → CLARIFY | ✅ Correct | ✅ Correct | ✅ test-001b | PASS |
| BUG_DIAGNOSIS no evidence → CLARIFY | ✅ Correct | ✅ Correct | ✅ test-002 | PASS |
| READINESS missing criteria → CLARIFY | ✅ Correct | ✅ Correct | ✅ test-004 | PASS |
| PATCH_PROPOSAL no paths → CLARIFY | ✅ Correct | ✅ Correct | ✅ test-005 | PASS |
| CODEBASE_QUESTION → ACCEPT_WITH_SAFE_DEFAULTS | ✅ Correct | ✅ Correct | ✅ test-003 | PASS |
| Security claim → CLARIFY/REJECT | ✅ Correct | ✅ Correct | ✅ test-009 | PASS |

## Safe-Default Verification

| Type | Safe Default | Required Condition | Bounded | Auditable |
|---|---|---|---|---|
| CODE_REVIEW | current_git_diff | has_diff AND has_working_tree | ✅ | ✅ Recorded in SafeDefaults |
| CODEBASE_QUESTION | bounded_repository_search | Always applied | ✅ (limit=20) | ✅ Recorded in SafeDefaults |
| BUG_DIAGNOSIS | None | N/A | ✅ | ✅ |
| READINESS_ASSESSMENT | None | N/A | ✅ | ✅ |
| PATCH_PROPOSAL | None | N/A | ✅ | ✅ |

All safe defaults are visible in the resulting `IntakeContract`. No default activates without its required evidence.

## Fail-Closed Verification

| Scenario | Behavior | Correct |
|---|---|---|
| Vague bug request ("Fix the bug.") | CLARIFY, HIGH risk | ✅ |
| Vague readiness ("Is this ready for production?") | CLARIFY, HIGH risk | ✅ |
| Vague patch ("Make the code better.") | CLARIFY, MEDIUM risk | ✅ |
| Empty request | CLARIFY, UNKNOWN type | ✅ |
| Single ambiguous word ("help") | CLARIFY, UNKNOWN type | ✅ |
| Explicit patch with LOW confidence | CLARIFY | ✅ |
| Mixed goals | CLARIFY | ✅ (partial — decomposition not always triggered) |

**No request silently becomes executable.** Ambiguity never becomes permission to execute.

## Model-Profile Placeholder Verification

| Profile | model_id | context_limit | enabled | Assessment |
|---|---|---|---|---|
| fast_model_profile | `""` | `0` | `True` | ⚠️ enabled=True with no model |
| deep_reasoning_model_profile | `""` | `0` | `True` | ⚠️ enabled=True with no model |
| fallback_model_profile | `""` | `0` | `True` | ⚠️ enabled=True with no model |

All profiles have empty `model_id` and zero operational limits, which is correct for provisional templates. However, `enabled=True` is misleading — these profiles are not operational. No code currently reads `enabled`, so there is no runtime safety risk in Phase 2A. The `enabled` field should be `False` until a real model is configured, but this is a design concern for later phases, not a Phase 2A safety defect.

Tests verify: `model_id == ""` and `context_limit == 0` for all profiles. ✅

## Test Coverage Assessment

| Scenario | Covered | Notes |
|---|---|---|
| CODE_REVIEW with diff | ✅ | test-001a |
| CODE_REVIEW without diff | ✅ | test-001b |
| BUG_DIAGNOSIS without evidence | ✅ | test-002 |
| CODEBASE_QUESTION | ✅ | test-003 |
| READINESS_ASSESSMENT without criteria | ✅ | test-004 |
| PATCH_PROPOSAL vague | ✅ | test-005 |
| Spanish CODE_REVIEW (with/without diff) | ✅ | test-006a, test-006b |
| Spanish BUG_DIAGNOSIS | ✅ | test-007 |
| Explicit patch with paths | ⚠️ | test-008 — assertion incorrect |
| Security/production claim | ✅ | test-009 |
| Mixed goals | ✅ | test-010 |
| Empty request | ✅ | test-class-01 |
| Single ambiguous word | ✅ | test-class-02 |
| Model profiles structure | ✅ | test-model-profiles |
| Model profiles model-agnostic | ✅ | test-model-profiles |
| Cache key structure | ✅ | test-model-profiles |
| ACCEPT_AS_IS outcome | ❌ | No test exercises this path |
| REJECT_UNSAFE_OR_UNSUPPORTED outcome | ❌ | No test exercises CRITICAL risk |
| Mixed goals decomposition detection gap | ❌ | No test for review+fix+readiness mix |

## Findings

| # | Severity | Finding | Evidence | Impact | Affected File:Line |
|---|---|---|---|---|---|
| F-01 | **MEDIUM** | Test `test_explicit_patch_request` assertion excludes CLARIFY for LOW-confidence PATCH_PROPOSAL | pytest output: `assert CLARIFY in (ACCEPT_AS_IS, REFINE_FOR_EXECUTION, ACCEPT_WITH_SAFE_DEFAULTS)` | Test fails; misrepresents intended behavior; CI broken | `agent_solution/tests/test_intake.py:196` |
| F-02 | **MEDIUM** | Mixed-goals detector uses keyword-count threshold (≥3) that misses many mixed requests | Smoke-10: "review+fix+readiness" → mixed=False; "review+fix" → mixed=False | Mixed requests not decomposed; user must self-separate | `agent_solution/intake/policy.py:60-76` |
| F-03 | **MEDIUM** | Mixed-goals keyword list omits "ready", "production", "better", "improve" | `_has_mixed_goals` keyword list at `policy.py:64-75` | Readiness+review or patch+question mixes undetected | `agent_solution/intake/policy.py:64-75` |
| F-04 | **LOW** | Model profiles have `enabled=True` with empty `model_id` and zero limits | `model_profile.py:39,54,69` | Misleading for future routing code; no runtime impact in Phase 2A | `agent_solution/intake/model_profile.py:39,54,69` |
| F-05 | **LOW** | Ruff reports 17 lint warnings (unused imports, import ordering, line length) | ruff output | Code hygiene; no correctness impact | Multiple files |
| F-06 | **INFO** | No test exercises `ACCEPT_AS_IS` or `REJECT_UNSAFE_OR_UNSUPPORTED` decision paths | test_intake.py | Coverage gap; behavior is correct but untested | `agent_solution/tests/test_intake.py` |

## Final Decision

**CHANGES_REQUIRED**

## Required Corrective Actions (Phase-02-FIX-01)

The following must be addressed before re-review:

1. **F-01 (MEDIUM):** Update `test_explicit_patch_request` assertion in `agent_solution/tests/test_intake.py:196` to include `IntakeDecision.CLARIFY` as an acceptable outcome, or provide the classifier with sufficient signals (e.g., has_diff=True) to achieve MEDIUM+ confidence for explicit patch requests.

2. **F-02 + F-03 (MEDIUM):** Either:
   - (a) Lower the mixed-goals threshold from 3 to 2 in `_has_mixed_goals` and expand the keyword list to include "ready", "production", "better", "improve", "change"; or
   - (b) Replace the keyword-count heuristic with a task-type overlap detector that checks whether the request text matches patterns from 2+ distinct task types; or
   - (c) Document the limitation explicitly in `docs/phase-02-intake-gate.md` and add a test that exercises the decomposition path for the specific mixed-goal patterns the system is designed to detect.

The minimum correct remediation is (c): document the limitation and add a focused test. The mixed-goals detector is a heuristic, and its gaps are safe (CLARIFY is still returned). The risk is that decomposition is not explicitly requested.

## Statement

No implementation files, benchmark files, benchmark results, or Phase-1 artifacts were modified during this review. Only review artifacts were created.
