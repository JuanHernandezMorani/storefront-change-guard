# Phase 04 — Isolated Patch Validation

## Status

Accepted after the recorded controlled live validation.

## Scope

- static unified-diff safety validation;
- detached temporary Git worktree creation;
- worktree-only patch preflight and application;
- named allowlisted validation commands;
- bounded command evidence and machine-readable JSON artifact;
- no model call, commit, merge, push, or source-checkout mutation.

## Recorded result

The controlled patch introduced `STANDARD_SHIPPING_CENTS` in root `shipping.py`
and added two behavior tests. It ran against base commit
`618851b4ec4ef5787fba1caf1b08f1aa7cbd415b`.

- Status: `VALIDATED`
- Source checkout unchanged: `true`
- Worktree creation, patch preflight, patch application, compileall, pytest,
  Ruff, diff check, and worktree cleanup: all passed
- Worktree retained: `false`

## Evidence

`artifacts/phase04-live/run-20260626-032234/phase04-f90b2e47f8c5.validation.json`

## Remaining boundary

Phase 04 validates a supplied correction. It does not authorize merge,
deployment, or source-checkout mutation. Those decisions remain outside Phase 04.
