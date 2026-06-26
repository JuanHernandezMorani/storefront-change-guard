# Phase-02-FIX-02 (post-review) — Narrow Spanish Review Pattern and Negative Patch Constraint

## Review Findings Addressed

| Finding | Severity | Description |
|---|---|---|
| F-01 | LOW | Spanish review regex contains Portuguese-oriented alternatives (`uma`, `õ`, `ã`) that broaden scope beyond intended Spanish-only behavior |
| F-02 | LOW | Missing constraint pattern for "do not apply" allows "Do not apply a patch." to trigger PATCH_PROPOSAL signal |

## Root Cause Analysis

### F-01 — Overly Broad Spanish Review Regex

**Root cause:** The Spanish review pattern `hac[ée] (una|uma) revis[io]?[áaóõã]?n?` included Portuguese alternatives `uma`, `õ`, and `ã` that were not part of the original Spanish-only design. This meant Portuguese-only phrasing such as "Faça uma revisão de shipping.py." could match the CODE_REVIEW classifier.

**Remediation:**
1. Replaced `(una|uma)` with `una` — only Spanish "una" is accepted.
2. Removed `õã` from the optional accent set `[áaóõã]` → `[áaó]`.
3. New pattern: `hac[ée] una revis[io]?[áaó]?n?` — narrow, valid Spanish only.

### F-02 — Missing "do not apply" Constraint

**Root cause:** The constraint-phrase list in `policy.py` included "without applying" but not "do not apply" or "don't apply". This allowed "Do not apply a patch." to match the PATCH_PROPOSAL pattern `\bpatch\b` without being stripped as a constraint.

**Remediation:**
1. Added `\bdo not apply\b` and `\bdon't apply\b` to `_CONSTRAINT_PATTERNS` in `policy.py`.
2. These patterns are stripped before classification so "Do not apply a patch." does not trigger PATCH_PROPOSAL.
3. Affirmative "Apply the patch to shipping.py." continues to match `\bapply\b.*\bpatch\b` in `_PATCH_PATTERNS`.

## Exact Implementation Changes

### agent_solution/intake/classifier.py

- Line 26: Replaced `r"\bhac[ée] (una|uma) revis[io]?[áaóõã]?n?\b"` with `r"\bhac[ée] una revis[io]?[áaó]?n?\b"`.
- No changes to other patterns or classification logic.

### agent_solution/intake/policy.py

- Added two new constraint patterns:
  - `re.compile(r"\bdo not apply\b", re.IGNORECASE)`
  - `re.compile(r"\bdon't apply\b", re.IGNORECASE)`
- No changes to classification or decision logic.

### agent_solution/tests/test_intake.py

- Added `TestNegativePatchConstraint` class with 3 tests:
  - `test_do_not_apply_patch` — "Do not apply a patch." → not PATCH_PROPOSAL
  - `test_review_do_not_apply_patch` — "Review shipping.py. Do not apply a patch." → CODE_REVIEW + ACCEPT_WITH_SAFE_DEFAULTS
  - `test_affirmative_patch_still_patch_proposal` — "Apply the patch to shipping.py." → PATCH_PROPOSAL
- Added `TestSpanishOnlyReviewPattern` class with 1 test:
  - `test_portuguese_not_code_review` — "Faça uma revisão de shipping.py." → not CODE_REVIEW

## Validation Summary

- `python -m compileall -q agent_solution` — PASS
- `python -m pytest agent_solution/tests/test_intake.py -v` — PASS (all tests including new)
- `python -m ruff check agent_solution` — PASS (0 errors)
- `git diff --check` — PASS (no whitespace errors)

## Audit Link

This post-review correction artifact.
