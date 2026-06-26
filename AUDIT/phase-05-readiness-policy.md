# Phase 05 — Deterministic Readiness Policy

## Status

Implementation and deterministic policy tests complete. A run with real Phase
03 and Phase 04 artifacts remains required before approval.

## Decision authority

Phase 05 consumes only prior machine-readable artifacts. It has no model call,
no patch-application capability, no shell execution, and no repository mutation.

`READY` requires a completed Phase 03 analysis, no HIGH/CRITICAL findings, a
`VALIDATED` Phase 04 artifact, and all recorded Phase 04 commands passing.

## Validation evidence

`test_readiness.py` covers positive readiness, incomplete analysis, severe
findings, missing validation, failed validation, failed commands, and artifact
round-tripping.
