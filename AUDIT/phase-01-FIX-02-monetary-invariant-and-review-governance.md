# Phase-01-FIX-02 — Monetary Invariant and Review Governance Remediation

## 1. Identification

| Field | Value |
|---|---|
| Identifier | `Phase-01-FIX-02` |
| Type | Corrective fix |
| Parent phase | `Phase-01` |
| Originating phase | `Phase-01` |
| Triggering review | `Phase-01-REVIEW-01` |
| Date | 2026-06-23 |
| Status | Implementation complete — pending Phase-01-REVIEW-02 |
| Branch | N/A (working tree) |
| Related files | `money.ts`, `shipping.ts`, `money.test.ts`, `shipping.test.ts`, `checkout-rules.md`, `POLICY-ADDENDUM-01-REVIEW-AND-IMMUTABILITY.md`, `review-register.md`, `change-register.md`, `CHANGELOG.md`, `README.md` |

---

## 2. Reason for Existence

This fix exists because `Phase-01-REVIEW-01` identified two blocking defects:

### Finding R01-02 — Monetary invariant not enforced

The checkout documentation states that internal business-rule calculations use integer cents. However, `calculateShipping(subtotalCents)` and `toDisplay(cents)` accepted fractional values such as `5000.5`, violating the documented domain contract. While the current UI produces integer cents through `toCents()`, the public domain functions do not enforce their documented contract, leaving them unsafe for future callers.

### Finding R01-01 — Missing review governance and inconsistent register

`AUDIT/FIX-POLICY.md` does not define review artifacts and references a non-existent `AUDIT/fix-register.md`. Without a dedicated review process, a phase can self-declare acceptance without independent validation, weakening auditability.

### Finding R01-03 — Phase-01 milestone overstates scope

The README states Phase-01 prepared controlled candidate changes, but the candidate change has not yet been created.

All three findings block final Phase-01 acceptance.

---

## 3. Scope Ownership

| Field | Value |
|---|---|
| Originating phase | `Phase-01` |
| Detection phase | `Phase-01` (independent review) |
| Affected files | `money.ts`, `shipping.ts`, `money.test.ts`, `shipping.test.ts`, `checkout-rules.md`, `POLICY-ADDENDUM-01-REVIEW-AND-IMMUTABILITY.md`, `review-register.md`, `change-register.md`, `CHANGELOG.md`, `README.md` |
| Affected behavior | Monetary-domain validation, review governance, documentation accuracy |
| Unrelated phases modified | None |

---

## 4. Evidence

### Monetary-domain evidence

`calculateShipping(5000.5)` executed without error, returning a shipping cost based on a fractional-cent input. `toDisplay(5000.5)` returned `50.005` without error. Both violate the documented integer-cent contract.

### Governance evidence

`AUDIT/FIX-POLICY.md` line 132 references `AUDIT/fix-register.md`. No such file exists. The actual register is `AUDIT/change-register.md`. No review artifact type is defined in the policy.

### Documentation evidence

`README.md` line 194 states Phase-01 prepared "controlled candidate changes." The candidate change has not been created.

---

## 5. Root Cause Analysis

### Monetary invariant — triggering condition

A caller passes a fractional-cent value (e.g. `5000.5`) to `calculateShipping()` or `toDisplay()`.

### Monetary invariant — immediate technical cause

`calculateShipping()` validated only finiteness and non-negativity. `toDisplay()` validated only finiteness and non-negativity. Neither function validated that the input was an integer. The `Number.isInteger()` check was missing from both functions.

### Monetary invariant — contributing factors

- The initial Phase-01 implementation focused on the shipping boundary rule (`>=` vs `>`) and did not add integer-cent enforcement.
- The `toCents()` function rounds to the nearest integer, so the UI path never produces fractional cents. The gap was invisible in the existing usage pattern.

### Monetary invariant — impact

The domain functions do not enforce their documented contract. A future caller passing `5000.5` would receive a result based on a half-cent, which is not a valid monetary representation in this domain.

### Governance — root cause

The original `FIX-POLICY.md` was written before the review governance pattern was identified. It defined three artifact types (Phase, FIX, ENHANCE) but not REVIEW. It referenced a placeholder register name (`fix-register.md`) that was never created; the actual register uses a different name (`change-register.md`).

### Why prior validation did not catch the defects

- The monetary defect was not exercised by the existing UI flow (which always uses `toCents()` output). It was found by code review, not by tests.
- The governance gap was structural — no review process existed to detect the absence of review artifacts.

---

## 6. Origin Classification

### Monetary-domain finding

| Field | Value |
|---|---|
| Origin | `ai_generated` |
| Model involvement | `direct` |
| Detection source | `code_review` |
| Severity | `medium` |
| Fix required | `yes` |
| Initial status | `open` |

### Governance finding

| Field | Value |
|---|---|
| Origin | `human_authored` |
| Model involvement | `none` |
| Detection source | `independent_review` |
| Severity | `high` |
| Fix required | `yes` |
| Initial status | `open` |

The monetary defect was generated with direct AI assistance. The governance gap is a structural omission in the original policy design, not attributable to a model.

---

## 7. Alternatives Considered

### Monetary validation alternatives

| Option | Description | Decision |
|---|---|---|
| A | Validate only in `calculateShipping`. | Rejected because `toDisplay` also accepts cent values and would still violate the invariant. |
| B | Create one reusable integer-cent validator in `money.ts` and use it in every cents-consuming domain function. | Selected. |
| C | Round fractional cents silently at each consumer. | Rejected because it hides invalid domain input and could alter business outcomes. |
| D | Represent amounts as display decimals throughout the domain. | Rejected because Phase-01 intentionally uses integer cents for deterministic money rules. |

### Governance alternatives

| Option | Description | Decision |
|---|---|---|
| A | Rewrite `AUDIT/FIX-POLICY.md` and historical reports. | Rejected because it would erase or alter historical evidence. |
| B | Create an explicit policy addendum plus append-only registers and review records. | Selected. |
| C | Treat each implementation report as its own acceptance authority. | Rejected because it prevents independent validation. |
| D | Keep no review register. | Rejected because review history would be difficult to audit. |

### Selected option rationale

Option B for both monetary and governance best supports the project priority order:

```text
Operability > Privacy > Response Time > Cost
```

A reusable validator is the most operable monetary solution: it centralizes the contract in one function, produces clear error messages, and is trivially testable. A policy addendum with append-only registers is the most operable governance solution: it preserves historical evidence, establishes clear review authority, and avoids destructive rewrites.

---

## 8. Implemented Solution

### Files created

| File | Purpose |
|---|---|
| `demo-storefront/src/domain/checkout/money.test.ts` | Focused tests for `assertNonNegativeIntegerCents`, `toDisplay`, and `toCents` |
| `AUDIT/POLICY-ADDENDUM-01-REVIEW-AND-IMMUTABILITY.md` | Policy addendum defining REVIEW artifacts, document immutability, and canonical registers |
| `AUDIT/review-register.md` | Append-only register of independent review outcomes |
| `AUDIT/phase-01-FIX-02-monetary-invariant-and-review-governance.md` | This fix audit |

### Files modified

| File | Change |
|---|---|
| `demo-storefront/src/domain/checkout/money.ts` | Added `assertNonNegativeIntegerCents()` helper; applied it to `toDisplay()` |
| `demo-storefront/src/domain/checkout/shipping.ts` | Replaced inline validation with `assertNonNegativeIntegerCents()` call |
| `demo-storefront/src/domain/checkout/shipping.test.ts` | Added fractional-cent rejection test case |
| `demo-storefront/docs/checkout-rules.md` | Appended "Integer-Cent Invariant" section |
| `AUDIT/change-register.md` | Appended `Phase-01-FIX-02` entry and updated metrics |
| `REPORT/changelog/CHANGELOG.md` | Appended `Phase-01-FIX-02` changelog entry |
| `README.md` | Appended "Documentation Correction — Phase 01 Scope" section |

### Files removed

None.

### Non-goals

- Shipping thresholds, fees, currency display behavior, and the inclusive `>=` boundary rule were not modified.
- No new dependencies were added.
- The controlled candidate change was not created.
- No Phase-02 or agent-scaffold work was modified.

---

## 9. Validation

All commands executed from `demo-storefront/` unless noted.

| Command | Working directory | Result |
|---|---|---|
| `npm ci` | `demo-storefront/` | Passed (13 upstream vulnerabilities, not addressed per constraints) |
| `npm run lint` | `demo-storefront/` | Passed (0 errors, 0 warnings) |
| `npm run build` | `demo-storefront/` | Passed (no warnings, build completes successfully) |
| `npm test` | `demo-storefront/` | Passed (13/13 tests: 6 shipping + 6 money + 1 provider-boundary) |
| `git diff --check` | Repository root | Passed (line-ending normalization warnings only, no whitespace errors) |

---

## 10. Acceptance Criteria

| Criterion | Result |
|---|---|
| Fractional-cent inputs rejected by `calculateShipping()` | Pass |
| Fractional-cent inputs rejected by `toDisplay()` | Pass |
| Existing below/equal/above shipping boundary behavior unchanged | Pass |
| Existing negative and non-finite validation unchanged | Pass |
| `toCents()` rounding behavior preserved | Pass |
| Focused automated tests verify the integer-cent invariant | Pass |
| Lint passes without suppression | Pass |
| Build passes without warnings | Pass |
| Policy addendum formally defines REVIEW and immutability rules | Pass |
| `AUDIT/change-register.md` declared canonical; `AUDIT/review-register.md` exists | Pass |
| README scope correction present without deleting historical evidence | Pass |
| No unrelated shipping or checkout behavior changed | Pass |
| No controlled candidate change introduced | Pass |
| Documentation and traceability artifacts updated | Pass |

---

## 11. Final Disposition

**Implementation complete — pending Phase-01-REVIEW-02**
