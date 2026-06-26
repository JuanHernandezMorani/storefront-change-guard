# Phase 04 — Isolated Patch Validation

## Status

Implementation and deterministic integration tests complete. A controlled
end-to-end invocation in the target Windows checkout remains required before
approval.

## Scope

- static unified-diff safety validation;
- detached temporary Git worktree creation;
- worktree-only patch preflight/application;
- named allowlisted validation commands;
- bounded command evidence and machine-readable JSON artifact;
- no model call, commit, merge, push, or source-branch mutation.

## Out of scope

- patch generation;
- arbitrary shell commands;
- auto-merge;
- Phase 05 readiness decision.

## Validation evidence

`test_patch_validation.py` verifies a valid patch, source-checkout immutability,
invalid path rejection, non-applying patch rejection, invalid base ref handling,
artifact privacy, and explicit retained-worktree behavior.
