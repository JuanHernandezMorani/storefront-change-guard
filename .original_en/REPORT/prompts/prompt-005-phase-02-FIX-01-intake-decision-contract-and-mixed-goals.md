# Prompt Report — Prompt 005: Phase-02-FIX-01 Intake Decision Contract and Mixed-Goals Detection

## Metadata

| Field | Value |
|---|---|
| Prompt ID | `prompt-005-phase-02-FIX-01-intake-decision-contract-and-mixed-goals` |
| Phase | Phase 2A — Request Intake and Prompt Quality Gate |
| Fix | Phase-02-FIX-01 |
| Task | Fix intake decision contract and mixed-goals detection |
| Date | 2026-06-24 |

## Prompt Summary

The fix was requested in response to the independent review at `AUDIT/phase-02A-review-01-intake-gate.md` with decision `CHANGES_REQUIRED`.  Three MEDIUM-severity findings required remediation:

1. **F-01:** Test `test_explicit_patch_request` excluded CLARIFY for LOW-confidence PATCH_PROPOSAL.
2. **F-02:** Mixed-goals detector used keyword-count threshold (≥3) that missed many mixed requests.
3. **F-03:** Mixed-goals keyword list omitted readiness and improvement signals.

## Implementation Approach

### F-01: Classifier Enhancement + Test Rewrite

Added validation-command and expected-behavior patterns to `_PATCH_PATTERNS` in the classifier, enabling HIGH-confidence classification for explicit patch requests with all required fields.  Rewrote the test into two classes: high-confidence (→ REFINE_FOR_EXECUTION) and low-confidence (→ CLARIFY).

### F-02/F-03: Signal-Overlap Detection

Replaced the keyword-count heuristic with deterministic task-signal overlap.  The new detector checks whether the request matches patterns from ≥2 distinct task types.  This is deterministic, auditable, and directly tied to the execution contracts.

### Ruff Remediation

Fixed all 17 Ruff warnings across the scoped files:
- Removed unused imports (5 F401)
- Fixed import ordering (5 I001)
- Fixed line length (1 E501)
- Fixed UP017 (datetime.UTC alias)
- Fixed UP037 (quoted annotation)
- Fixed F821 (undefined name)

## Files Modified

| File | Changes |
|---|---|
| `agent_solution/intake/classifier.py` | Added 6 patterns to `_PATCH_PATTERNS` |
| `agent_solution/intake/policy.py` | Replaced mixed-goals detector, fixed imports, added scope resolution, added blocking reasons |
| `agent_solution/intake/clarifier.py` | Updated mixed-goals decomposition question |
| `agent_solution/intake/models.py` | Removed unused imports, fixed datetime.UTC |
| `agent_solution/intake/defaults.py` | Removed unused import |
| `agent_solution/tests/test_intake.py` | Rewrote test-008, added 7 new test classes |
| `docs/phase-02-intake-gate.md` | Added patch contract, mixed-goals detection, worktree invariant sections |

## Validation

All validation commands pass:
- compileall: PASS
- pytest: 28/28 PASS
- ruff: 0 errors
- agent CLI help: PASS
- git diff --check: PASS

All 8 manual smoke cases pass with expected behavior.
