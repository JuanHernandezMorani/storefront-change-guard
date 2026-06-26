# Audit Trail

This directory contains phase-based engineering audits for the prototype.

Each audit should document:

- Phase objective and scope.
- Inputs reviewed.
- Decisions made and rationale.
- Implemented changes.
- Validation commands executed.
- Results, failures, and known limitations.
- Risks carried to the next phase.
- Explicit exit criteria and whether they were met.

## Audit naming convention

```text
phase-00-repository-baseline.md
phase-01-demo-storefront-preparation.md
phase-02-agent-core.md
phase-03-local-model-integration.md
phase-04-patch-validation.md
phase-05-end-to-end-validation.md
phase-06-delivery-readiness.md
```

Audits are concise engineering records, not raw terminal logs. Raw output or run-specific evidence belongs in `REPORT/executions/` or `artifacts/`.
