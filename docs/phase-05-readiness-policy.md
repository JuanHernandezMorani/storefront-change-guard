# Phase 05 — Deterministic Readiness Policy

## Purpose

Phase 05 converts already-existing machine-readable evidence into an auditable
readiness result. It does not invoke an LLM, apply a patch, execute a test, or
mutate a repository.

Inputs are limited to:

1. one Phase 03 structured analysis JSON artifact; and
2. one Phase 04 patch-validation JSON artifact.

## Policy rules

`READY` requires all of the following:

1. Phase 03 status is `ANALYSIS_COMPLETED` or `ANALYSIS_CACHE_HIT`.
2. Phase 03 has a valid findings list.
3. No Phase 03 finding has `HIGH` or `CRITICAL` severity.
4. Phase 04 exists and has status `VALIDATED`.
5. Every recorded Phase 04 command has exit code `0` and no timeout.

The policy returns `NOT_READY`, `INSUFFICIENT_EVIDENCE`, or `INVALID_INPUT`
when those conditions are not met.

## Recorded live decision

| Field | Recorded value |
|---|---|
| Decision ID | `phase05-5c01c0f109ec` |
| Status | `READY` |
| Policy version | `phase-05.1.0` |
| Reason code | `ALL_REQUIRED_GATES_PASSED` |
| Source checkout unchanged | `true` |
| Model invocation | none |

Artifact: `artifacts/phase05-live/run-20260626-033155/phase05-5c01c0f109ec.readiness.json`.

The runner canonicalizes its supplied JSON inputs to UTF-8 without a BOM before
calling the Python CLI. This preserves semantic content while avoiding
PowerShell-specific encoding differences in copied artifacts.

## CLI

```powershell
python -m agent_solution readiness `
  --analysis-artifact .\artifacts\analysis.json `
  --patch-validation-artifact .\artifacts\phase04.validation.json `
  --artifact-dir .\artifacts
```

The emitted artifact contains the policy version, hashes of both inputs, status,
and reason codes. `READY` is not merge, deployment, or production authority.
