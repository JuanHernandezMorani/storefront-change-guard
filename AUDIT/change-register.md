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
