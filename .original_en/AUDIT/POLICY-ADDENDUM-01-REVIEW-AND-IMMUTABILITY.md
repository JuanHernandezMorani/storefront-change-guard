# Policy Addendum 01 — Review Governance and Document Immutability

**Date:** 2026-06-23
**Supplements:** `AUDIT/FIX-POLICY.md`
**Precedence:** Takes precedence over conflicting parts of `AUDIT/FIX-POLICY.md` for review governance and register naming.

---

## 1. Canonical Identifier Set

The project uses four artifact types:

```text
Phase-NN
Phase-NN-FIX-NN
Phase-NN-ENHANCE-NN
Phase-NN-REVIEW-NN
```

### Identifier Meaning

| Identifier | Meaning |
|---|---|
| `Phase-NN` | A planned implementation phase that introduces a new capability, integration, or validated scope of work. |
| `Phase-NN-FIX-NN` | A corrective action required because a defect, failed validation, missing requirement, incorrect behavior, or blocking quality issue exists in work owned by `Phase-NN`. |
| `Phase-NN-ENHANCE-NN` | A non-blocking visual, aesthetic, UX, presentation, or usability improvement related to work owned by `Phase-NN`. |
| `Phase-NN-REVIEW-NN` | An independent acceptance review that evaluates one or more phase-owned implementations, fixes, or enhancements and decides whether they are approved, rejected, deferred, or require changes. |

---

## 2. Review as Acceptance Authority

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

---

## 3. Document Immutability

6. Existing historical records remain immutable. Do not delete, rewrite, replace, or sanitize earlier evidence.
7. Existing fixes or enhancements created before this addendum retain their historical text. Their review outcome is recorded by a dedicated review artifact rather than by rewriting old reports.

---

## 4. Canonical Registers

8. `AUDIT/change-register.md` is the canonical register for fixes and enhancements. `AUDIT/fix-register.md` is deprecated and must not be created.
9. `AUDIT/review-register.md` is the canonical append-only register for review outcomes.
10. `AUDIT/change-register.md`, `AUDIT/review-register.md`, and `REPORT/changelog/CHANGELOG.md` are living append-only indexes. Existing entries must not be edited or removed.
11. Root `README.md` and other operational documentation may receive append-only dated corrections or addenda; earlier historical statements must remain preserved.

---

## 5. Review Content Requirements

12. A review must record the reviewed artifacts, evidence, validation procedure, findings, decision, and final phase-status authority.

---

## 6. Examples

### Example 1: Defect ownership across phases

A defect introduced by Phase-02 but discovered during Phase-05 is remediated as `Phase-02-FIX-NN`, not as a Phase-05 fix. The discovery phase does not change ownership.

```text
Originating phase: Phase-02
Detected during: Phase-05
Remediation identifier: Phase-02-FIX-01
```

### Example 2: Phase acceptance after review

`Phase-01-REVIEW-02` may approve Phase-01 after reviewing `Phase-01-FIX-02`. The approving review records the final acceptance decision. The Phase-01 preparation report receives only a final-status update citing `Phase-01-REVIEW-02`.
