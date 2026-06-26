# Prompt Record — prompt-003-phase-01-FIX-02-monetary-invariant-and-review-governance

## Metadata

- **Date:** 2026-06-23
- **Tool / model:** OpenCode / local Nemotron 3
- **Purpose:** Corrective remediation of monetary-domain invariant and review-governance gaps
- **Relevant project phase:** Phase-01
- **Sensitive content removed:** Yes

## Prompt summary

A detailed remediation specification was provided requesting two corrective workstreams for Phase-01: (1) enforcing the integer-cent monetary invariant in the checkout domain by creating a reusable validation helper and applying it to all cents-consuming functions, with focused tests; and (2) establishing review governance through a policy addendum, review register, change-register update, README scope correction, and changelog entry. The specification defined strict scope boundaries limiting changes to Phase-01-owned files only.

## Input context supplied

- Current state of `money.ts`, `shipping.ts`, `shipping.test.ts`, `checkout-rules.md`
- `AUDIT/FIX-POLICY.md`, `AUDIT/phase-01-review-01.md`, `AUDIT/change-register.md`
- `README.md`, `REPORT/changelog/CHANGELOG.md`
- Findings R01-01 through R01-04 from Phase-01-REVIEW-01
- Scope boundaries (in-scope and out-of-scope items)
- Required technical remediation steps for both monetary and governance fixes

## Output summary

- `assertNonNegativeIntegerCents()` helper added to `money.ts` and applied to `calculateShipping()` and `toDisplay()`
- `money.test.ts` created with focused integer-cent invariant tests
- `shipping.test.ts` updated with fractional-cent rejection test
- Policy addendum created defining REVIEW artifacts, document immutability, and canonical registers
- Review register created with Phase-01-REVIEW-01 entry
- Change register updated with Phase-01-FIX-02 entry
- Changelog updated with Phase-01-FIX-02 entries
- README updated with append-only scope correction
- Fix audit, prompt traceability, and validation evidence created

## Author review and disposition

- Pending independent review (Phase-01-REVIEW-02)
- Reason: Implementation complete; awaiting independent validation and acceptance decision

## Resulting project change or decision

- Fractional-cent values are now rejected by all cents-consuming domain functions
- Review governance is formally defined through a policy addendum
- Canonical change and review registers are established
- Phase-01 scope documentation is corrected

## Validation performed

- `npm ci` from `demo-storefront/` — passed
- `npm run lint` from `demo-storefront/` — passed
- `npm run build` from `demo-storefront/` — passed
- `npm test` from `demo-storefront/` — passed (13/13 tests)
- `git diff --check` from repository root — passed
