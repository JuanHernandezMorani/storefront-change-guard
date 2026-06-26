# Phase 05 — Deterministic Readiness Policy

## Purpose

Phase 05 converts evidence that already exists into an auditable readiness
outcome. It does not invoke an LLM, apply a patch, execute a test, or mutate a
repository.

Inputs are only:

1. a Phase 03 structured analysis JSON artifact; and
2. a Phase 04 machine-readable patch-validation JSON artifact.

## Policy Rules

A change is `READY` only when all of the following are true:

1. Phase 03 status is `ANALYSIS_COMPLETED` or `ANALYSIS_CACHE_HIT`.
2. The Phase 03 artifact has a valid `findings` list.
3. The analysis contains no `HIGH` or `CRITICAL` findings.
4. Phase 04 artifact exists and has `status: VALIDATED`.
5. Every recorded Phase 04 command has `exit_code: 0` and `timed_out: false`.

The policy returns `NOT_READY` for unresolved severe findings or a failed patch
validation. It returns `INSUFFICIENT_EVIDENCE` when the required analysis or
validation evidence is absent or incomplete. It returns `INVALID_INPUT` for an
artifact that is not a JSON object or violates the expected minimal shape.

## CLI

```powershell
python -m agent_solution readiness `
  --analysis-artifact .\artifacts\analysis.json `
  --patch-validation-artifact .\artifacts\phase04.validation.json `
  --artifact-dir .\artifacts
```

The command emits and writes a JSON artifact containing:

- a stable policy version;
- SHA-256 fingerprints of both input artifacts;
- `READY`, `NOT_READY`, `INSUFFICIENT_EVIDENCE`, or `INVALID_INPUT`;
- structured reason codes and human-readable details.

## Authority Boundary

Phase 05 is intentionally conservative. A language model may have written the
Phase 03 review, but it never controls the Phase 05 result. Policy conditions
and Phase 04 command outcomes are the decision authority.
