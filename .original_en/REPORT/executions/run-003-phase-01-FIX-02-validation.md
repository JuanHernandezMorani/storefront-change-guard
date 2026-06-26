# Execution Record — run-003-phase-01-FIX-02-validation

## Metadata

- **Date/time:** 2026-06-23
- **Phase:** Phase-01-FIX-02
- **Repository revision:** Working tree (uncommitted)
- **Scenario / input:** Post-remediation validation of monetary invariant and governance fixes
- **Policy version:** FIX-POLICY.md v1 + POLICY-ADDENDUM-01
- **Model configuration summary:** OpenCode with local Nemotron 3

## Commands executed

| Command | Working directory | Exit code | Result summary |
|---|---|---|---|
| `npm ci` | `demo-storefront/` | 0 | 248 packages installed; 13 upstream vulnerabilities (not addressed) |
| `npm run lint` | `demo-storefront/` | 0 | 0 errors, 0 warnings |
| `npm run build` | `demo-storefront/` | 0 | TypeScript compilation succeeded; Vite build succeeded; no warnings |
| `npm test` | `demo-storefront/` | 0 | 13/13 tests passed (6 shipping + 6 money + 1 provider-boundary) |
| `git diff --check` | Repository root | 0 | Line-ending normalization warnings only; no whitespace errors |

## Outcome

All validation commands passed. Fractional-cent values (e.g. `5000.5`) are rejected by both `calculateShipping()` and `toDisplay()` with the exact required error messages. Existing shipping boundary behavior is unchanged. No controlled candidate change was introduced.

## Final result table

| Criterion | Result |
|---|---|
| `npm run lint` passes | Pass |
| `npm run build` passes | Pass |
| `npm test` passes (13/13) | Pass |
| Fractional-cent values rejected | Pass |
| Existing shipping behavior unchanged | Pass |
| `git diff --check` passes | Pass |
| No controlled candidate change introduced | Pass |

## Test count

- Total test files: 3
- Total tests: 13
- New tests added by this fix: 7 (6 in `money.test.ts` + 1 in `shipping.test.ts`)

## Artifact references

- Remediation audit: `AUDIT/phase-01-FIX-02-monetary-invariant-and-review-governance.md`
- Prompt traceability: `REPORT/prompts/prompt-003-phase-01-FIX-02-monetary-invariant-and-review-governance.md`
- Change register: `AUDIT/change-register.md`
- Review register: `AUDIT/review-register.md`
- Policy addendum: `AUDIT/POLICY-ADDENDUM-01-REVIEW-AND-IMMUTABILITY.md`

## Limitations / follow-up

- No new dependencies were added; all tests use existing Vitest and `react-dom/server`.
- This fix is pending independent review by `Phase-01-REVIEW-02`.
- Git commit SHA and clean working-tree state must be verified during `Phase-01-REVIEW-02`.
