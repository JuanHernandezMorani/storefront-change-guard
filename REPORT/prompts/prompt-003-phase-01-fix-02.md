You are working inside the repository:

`C:\Proyectos\storefront-change-guard`

Perform a narrow, fully documented corrective remediation for the Phase-01 work only.

# Work Identification

| Field | Value |
|---|---|
| Identifier | `Phase-01-FIX-02` |
| Type | Corrective fix |
| Title | `Monetary Invariant and Review Governance Remediation` |
| Parent phase | `Phase-01` |
| Originating phase | `Phase-01` |
| Triggering review | `Phase-01-REVIEW-01` |
| Current completion state | Not started |
| Final acceptance authority | `Phase-01-REVIEW-02` |

This remediation belongs strictly to `Phase-01`.

Do not use this work to modify, correct, redesign, or improve work owned by another phase. In particular, do not create the controlled candidate regression, do not implement the review agent, and do not change the agent CLI or Phase-02 planning.

# Mandatory Reading Before Changes

Read these files before changing anything:

```text
AUDIT/FIX-POLICY.md
AUDIT/phase-01-demo-storefront-preparation.md
AUDIT/phase-01-FIX-01-context-boundary-remediation.md
AUDIT/phase-01-REVIEW-01-phase-closure-and-governance.md
AUDIT/change-register.md
README.md
demo-storefront/docs/checkout-rules.md
demo-storefront/src/domain/checkout/money.ts
demo-storefront/src/domain/checkout/shipping.ts
demo-storefront/src/domain/checkout/shipping.test.ts
```

Inspect the current source and tests before deciding exact edits.

# Governing Rules

## 1. Strict Phase Ownership

Everything implemented in this remediation must belong to `Phase-01`.

The remediation may correct:

- Phase-01 checkout-domain behavior.
- Phase-01 tests.
- Phase-01 documentation accuracy.
- Phase-01 acceptance governance and traceability gaps exposed by `Phase-01-REVIEW-01`.

It must not correct or implement work owned by Phase-00, Phase-02, or later phases.

## 2. Historical Documentation Is Immutable

Do not delete, replace, rewrite, reformat, or silently alter prior historical evidence.

The following existing records are immutable and must not be edited in this fix:

```text
AUDIT/FIX-POLICY.md
AUDIT/phase-00-repository-baseline.md
AUDIT/phase-01-demo-storefront-preparation.md
AUDIT/phase-01-FIX-01-context-boundary-remediation.md
AUDIT/phase-01-REVIEW-01-phase-closure-and-governance.md
REPORT/prompts/prompt-001-phase-01-storefront-preparation.md
REPORT/prompts/prompt-002-phase-01-FIX-01-context-boundary-remediation.md
REPORT/executions/run-002-phase-01-FIX-01-validation.md
```

Do not update the final status of the Phase-01 preparation report during this fix. The status may be changed only after `Phase-01-REVIEW-02` independently approves Phase-01.

For living documentation files, use append-only updates:

```text
AUDIT/change-register.md
REPORT/changelog/CHANGELOG.md
README.md
demo-storefront/docs/checkout-rules.md
```

Do not remove or rewrite older content in those files. Add clearly dated sections or entries that preserve the original evidence.

## 3. No Self-Acceptance

This fix must not declare itself accepted.

Its final implementation status must be:

```text
Implementation complete — pending Phase-01-REVIEW-02
```

Only `Phase-01-REVIEW-02` may decide whether `Phase-01-FIX-02` and Phase-01 are accepted.

## 4. Existing Constraints

Do not:

- Run `npm audit fix`.
- Upgrade unrelated dependencies.
- Add a backend, database, Docker, cloud service, vector store, authentication, or agent framework.
- Add broad UI, snapshot, browser, end-to-end, or visual-regression test infrastructure.
- Add `jsdom`, React Testing Library, Playwright, Cypress, or any dependency not directly required by the focused domain tests.
- Change free-shipping threshold, standard-shipping fee, currency display behavior, or the inclusive `>=` boundary rule.
- Modify upstream attribution or license files.
- Create or amend Git commits.
- Modify the `agent_solution` package or its CLI.
- Create the controlled buggy candidate change.
- Suppress a lint, TypeScript, Vite, esbuild, or test failure.

# Required Remediation A — Enforce the Integer-Cent Monetary Invariant

## Problem

Phase-01 documentation states that internal business-rule calculations use integer cents. A cent cannot be divided into a fraction.

The current code accepts fractional values such as:

```ts
calculateShipping(5000.5)
toDisplay(5000.5)
```

Those calls violate the documented monetary domain because `5000.5` represents half a cent.

## Required Behavior

Every public function that accepts an amount already expressed in cents must reject values that are not:

1. Finite.
2. An integer.
3. Non-negative.

`toCents(displayAmount)` is different: it accepts a display amount and converts it to the nearest integer cent. Preserve its existing documented rounding behavior unless a directly related defect is proven.

## Required Implementation

Create one reusable, framework-independent validation helper in:

```text
demo-storefront/src/domain/checkout/money.ts
```

Use a clear name equivalent to:

```ts
assertNonNegativeIntegerCents(cents: number, label?: string): void
```

The helper must reject values in this order:

1. Non-finite values.
2. Non-integer values.
3. Negative values.

Use clear errors. The preferred contract is:

```text
Subtotal must be a finite number
Subtotal must be an integer
Subtotal must not be negative

Cents must be a finite number
Cents must be an integer
Cents must not be negative
```

Use the helper in both places that consume an integer-cent input:

- `calculateShipping(subtotalCents)` in `shipping.ts`, using the label `Subtotal`.
- `toDisplay(cents)` in `money.ts`, using the default label `Cents`.

Do not duplicate equivalent validation logic across files.

## Required Tests

Add focused tests that prove:

1. `calculateShipping(5000.5)` throws the exact integer-validation error.
2. Existing below-threshold, equal-threshold, and above-threshold shipping behavior remains unchanged.
3. Existing negative and non-finite shipping validation remains correct.
4. `toDisplay(5000.5)` throws the exact integer-validation error.
5. A valid whole-cent conversion still works, for example `toDisplay(5000) === 50`.

Use Vitest only. Do not add new dependencies.

A small new `money.test.ts` file is acceptable if it keeps the tests focused and readable.

## Documentation Update

Append a new section to:

```text
demo-storefront/docs/checkout-rules.md
```

The new section must be titled exactly:

```text
## Integer-Cent Invariant
```

It must state:

- Internal amounts expressed in cents must be finite, non-negative integers.
- Fractional-cent values are invalid.
- `5000.5` cents is rejected because a cent cannot be divided into a half-cent in this domain.
- Display amounts are converted by `toCents()` and rounded to the nearest whole cent before business rules use them.

Do not modify existing sections; append this section only.

# Required Remediation B — Review Governance and Traceability

## Problem

`Phase-01-REVIEW-01` found that the current policy does not define review artifacts, the current policy references a non-existent `AUDIT/fix-register.md`, and the project needs an explicit mechanism through which a phase, fix, or enhancement is independently approved or rejected.

## Required New Policy Addendum

Do not edit `AUDIT/FIX-POLICY.md`.

Create this new file:

```text
AUDIT/POLICY-ADDENDUM-01-REVIEW-AND-IMMUTABILITY.md
```

Write it in English.

The addendum must declare that it supplements and takes precedence over conflicting parts of `AUDIT/FIX-POLICY.md` for review governance and register naming.

It must define the canonical identifier set:

```text
Phase-NN
Phase-NN-FIX-NN
Phase-NN-ENHANCE-NN
Phase-NN-REVIEW-NN
```

It must define `Phase-NN-REVIEW-NN` as an independent acceptance artifact with these rules:

1. Every completed Phase, FIX, or ENHANCE requires an independent REVIEW before it can be considered finally accepted.
2. A review may evaluate one phase-owned implementation, one or more phase-owned fixes or enhancements, or their combined final state.
3. A review must use one of these outcomes:

```text
APPROVED
CHANGES_REQUIRED
REJECTED
DEFERRED
```

4. A review is the authority that approves or rejects a phase, fix, or enhancement. Implementation reports must not self-authorize final acceptance.
5. After an `APPROVED` review, the only allowed mutation of the original phase preparation report is a final-status update that cites the approving review identifier.
6. Existing historical records remain immutable. Do not delete, rewrite, replace, or sanitize earlier evidence.
7. Existing fixes or enhancements created before this addendum retain their historical text. Their review outcome is recorded by a dedicated review artifact rather than by rewriting old reports.
8. `AUDIT/change-register.md` is the canonical register for fixes and enhancements. `AUDIT/fix-register.md` is deprecated and must not be created.
9. `AUDIT/review-register.md` is the canonical append-only register for review outcomes.
10. `AUDIT/change-register.md`, `AUDIT/review-register.md`, and `REPORT/changelog/CHANGELOG.md` are living append-only indexes. Existing entries must not be edited or removed.
11. Root `README.md` and other operational documentation may receive append-only dated corrections or addenda; earlier historical statements must remain preserved.
12. A review must record the reviewed artifacts, evidence, validation procedure, findings, decision, and final phase-status authority.

The addendum must include a concise example showing that a defect introduced by Phase-02 but discovered during Phase-05 is remediated as `Phase-02-FIX-NN`, not as a Phase-05 fix.

It must also include a concise example that `Phase-01-REVIEW-02` may approve Phase-01 after reviewing `Phase-01-FIX-02`.

## Required Review Register

Create this new append-only file:

```text
AUDIT/review-register.md
```

Write it in English.

It must contain:

### Purpose

A concise explanation that it records independent review outcomes without overwriting underlying evidence.

### Review Records

Create the first entry for the already-created review:

| Field | Required value |
|---|---|
| Review ID | `Phase-01-REVIEW-01` |
| Parent phase | `Phase-01` |
| Reviewed targets | `Phase-01`, `Phase-01-FIX-01` |
| Outcome | `CHANGES_REQUIRED` |
| Approved targets | `Phase-01-FIX-01` |
| Unapproved target | `Phase-01` |
| Required next action | `Phase-01-FIX-02` followed by `Phase-01-REVIEW-02` |
| Audit link | Relative link to `phase-01-REVIEW-01-phase-closure-and-governance.md` |

### Update Rules

State that new review records are appended and no earlier review record is changed or removed.

## Required Change Register Update

Append, without editing existing entries, a dated `Phase-01-FIX-02` section to:

```text
AUDIT/change-register.md
```

It must include:

- Identifier: `Phase-01-FIX-02`.
- Parent and originating phase: `Phase-01`.
- Type: Fix.
- Triggering review: `Phase-01-REVIEW-01`.
- Scope: integer-cent invariant and review-governance remediation.
- Monetary-domain finding classification: `ai_generated`, model involvement `direct`, detection source `code_review`, severity `medium`.
- Governance finding classification: `human_authored`, model involvement `none`, detection source `independent_review`, severity `high`.
- Status: `Implementation complete — pending Phase-01-REVIEW-02` after validation succeeds.
- Relative link to the new fix audit.

Do not edit, remove, reorder, or recalculate any earlier metrics or rows. If a new metric snapshot is useful, append a clearly dated update section rather than changing historical values.

## Required README Correction

Do not edit or delete the existing Phase-01 milestone row.

Append this new dated section to the root `README.md`:

```text
## Documentation Correction — Phase 01 Scope
```

The content must state that:

- Phase-01 prepared a clean, documented, testable checkout baseline.
- Phase-01 did not create the controlled buggy candidate change.
- The future controlled candidate change remains intentionally scheduled for the agent-review scenario phase.
- The earlier milestone wording is preserved as historical documentation and is clarified by this correction.

## Required Changelog Update

Append a distinct `Phase-01-FIX-02` entry to:

```text
REPORT/changelog/CHANGELOG.md
```

Do not remove or rewrite earlier changelog entries.

The new entry must summarize:

- Integer-cent validation for shipping and display conversions.
- Focused fractional-cent tests.
- Review governance addendum.
- Canonical change and review registers.
- Append-only documentation correction.
- Pending independent `Phase-01-REVIEW-02` acceptance.

# Required Fix Evidence

## 1. Fix Audit

Create:

```text
AUDIT/phase-01-FIX-02-monetary-invariant-and-review-governance.md
```

Write it in English.

It must include:

- Identification and parent-phase ownership.
- Triggering review reference: `Phase-01-REVIEW-01`.
- Two separate findings: monetary invariant and governance/traceability.
- Exact reason the fix exists.
- Technical root-cause analysis for the fractional-cent acceptance.
- Governance root-cause analysis for missing review authority and register inconsistency.
- Explicit distinction between the two origin classifications.
- Alternatives considered for monetary validation:

| Option | Description | Decision |
|---|---|---|
| A | Validate only in `calculateShipping`. | Rejected because `toDisplay` also accepts cent values and would still violate the invariant. |
| B | Create one reusable integer-cent validator in `money.ts` and use it in every cents-consuming domain function. | Selected. |
| C | Round fractional cents silently at each consumer. | Rejected because it hides invalid domain input and could alter business outcomes. |
| D | Represent amounts as display decimals throughout the domain. | Rejected because Phase-01 intentionally uses integer cents for deterministic money rules. |

- Alternatives considered for governance:

| Option | Description | Decision |
|---|---|---|
| A | Rewrite `AUDIT/FIX-POLICY.md` and historical reports. | Rejected because it would erase or alter historical evidence. |
| B | Create an explicit policy addendum plus append-only registers and review records. | Selected. |
| C | Treat each implementation report as its own acceptance authority. | Rejected because it prevents independent validation. |
| D | Keep no review register. | Rejected because review history would be difficult to audit. |

- Selected-solution rationale tied to:

```text
Operability > Privacy > Response Time > Cost
```

- Files created, modified, and removed.
- Scope boundaries and non-goals.
- Actual validation results.
- Acceptance criteria.
- Final disposition exactly:

```text
Implementation complete — pending Phase-01-REVIEW-02
```

Do not mark this fix as Accepted.

## 2. Prompt Traceability

Create:

```text
REPORT/prompts/prompt-003-phase-01-FIX-02-monetary-invariant-and-review-governance.md
```

Write it in English.

Include:

- Date.
- Identifier and parent phase.
- Tool: OpenCode.
- Model: local Nemotron 3.
- Objective.
- High-level task summary.
- Explicit scope boundaries.
- Statement that AI assistance was used for implementation support only.
- Statement that the repository author must independently review and validate the resulting work.
- Statement that no raw chain-of-thought, credentials, secrets, or unnecessary private-machine details are committed.

Do not include the raw full prompt.

## 3. Validation Evidence

Create:

```text
REPORT/executions/run-003-phase-01-FIX-02-validation.md
```

Write it in English.

Include:

- Identifier.
- Date.
- Environment summary without credentials or secrets.
- Exact commands executed.
- Working directory for each command.
- Actual summarized results.
- Actual test count.
- Explicit confirmation that fractional-cent values are rejected.
- Explicit confirmation that no controlled candidate change was introduced.
- Final outcome: implementation complete, pending `Phase-01-REVIEW-02`.

Do not fabricate test counts, command results, timings, or Git information.

# Required Validation Procedure

After implementing the remediation, run these commands.

From `demo-storefront/`:

```powershell
npm ci
npm run lint
npm run build
npm test
```

From repository root:

```powershell
git diff --check
```

If a command fails:

1. Investigate the real cause.
2. Correct only work owned by `Phase-01-FIX-02`.
3. Re-run the failed command.
4. Record only actual observed outcomes.
5. Do not bypass, suppress, or downgrade a failure.

# Final Response Format

When complete, provide a concise implementation report with:

1. Identifier and current disposition.
2. Files created.
3. Files modified.
4. Files removed.
5. Monetary-domain root cause and implemented solution.
6. Governance root cause and implemented solution.
7. Alternatives considered and selected option rationale.
8. Exact validation commands run.
9. Actual validation outcomes and test count.
10. New dependency status.
11. Confirmation that no controlled candidate change was created.
12. Deferred work.
13. Recommended Git commit message.

Do not create, amend, merge, or push any Git commit.
