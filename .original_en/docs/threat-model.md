# Threat Model and Trust Boundaries — Initial Direction

## Assets to protect

- Source code and business logic.
- Local environment configuration and credentials.
- Integrity of the candidate branch.
- Integrity of validation results.
- Developer trust in review findings and readiness decisions.

## Key threats and mitigations

| Threat | Mitigation |
|---|---|
| Sensitive code leaves the machine | Local-first endpoint; remote model use disabled by default. |
| Model invents a defect | Evidence must match a real file, line, and excerpt before a finding is accepted. |
| Model claims validation passed without evidence | Only controlled command results determine validation state. |
| Suggested patch damages working code | Patch applies only in a temporary Git worktree, never directly to the candidate branch. |
| Model requests unsafe commands | No arbitrary model-generated shell execution; commands are allowlisted by the implementation. |
| Secrets appear in artifacts or prompt records | `.env` is ignored; report conventions require redaction and no secret capture. |
| Overly broad repository exposure | Context builder limits inputs to diff, related files, tests, docs, and check output. |

## Residual risks

- A local model can still produce incorrect advice; all advice remains reviewable and evidence-bound.
- Dependency installation may execute package lifecycle scripts; baseline auditing must document package-manager behavior.
- A repository-specific test suite can be incomplete; the readiness policy must state exactly what was and was not verified.
