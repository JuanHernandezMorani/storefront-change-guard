# Demo Scenarios — Initial Plan

## Scenario A — Controlled free-shipping boundary regression

### Business rule

Free shipping applies when cart subtotal is **equal to or greater than** a configured threshold.

### Intended candidate regression

A candidate change uses a strict comparison (`>`) instead of an inclusive comparison (`>=`). This incorrectly charges shipping when the subtotal is exactly equal to the threshold.

### Expected prototype behavior

1. Collect the candidate diff and related checkout context.
2. Read the relevant business-rule documentation and tests.
3. Identify the boundary-condition defect with file and line evidence.
4. Explain user and business impact.
5. Propose an isolated minimal correction.
6. Add or identify a boundary test for the exact threshold.
7. Validate the proposed correction in a temporary worktree.
8. Mark the original candidate change as `NEEDS_CHANGES` or `BLOCKED` until the developer applies an accepted correction.

## Scenario B — Ready candidate

A follow-up candidate change includes the inclusive comparison and passing boundary test. The system should report `READY` or `READY_WITH_NOTES` only when deterministic checks and policy conditions support that outcome.

## Scenario design constraints

- Each scenario must be reproducible from a documented commit or branch.
- The defect must be intentionally introduced after baseline audit.
- Output must distinguish an original candidate branch from an independently validated proposed patch.
- Claims about upstream code must remain accurate and attributable.
