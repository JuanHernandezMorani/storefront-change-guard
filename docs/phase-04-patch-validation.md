# Phase 04 — Isolated Patch Validation

## Purpose

Phase 04 validates a supplied unified diff without modifying the source checkout,
its current branch, index, or commit history. It contains no model invocation.

```text
validated patch input
→ static patch safety checks
→ detached temporary Git worktree
→ git apply --check
→ git apply
→ named allowlisted commands
→ machine-readable validation artifact
```

## Safety Contract

- The original repository is read only for the full Phase 04 run.
- The patch is applied only to a detached temporary worktree created from an
  explicit Git ref, defaulting to `HEAD`.
- Shell interpolation is forbidden. Every command is an argument array.
- Arbitrary model-generated commands are forbidden.
- Binary patches, path traversal, Git metadata paths, sensitive filenames,
  rename/copy patches, and oversized patches are rejected before worktree
  creation.
- The validation artifact contains a patch SHA-256, changed-path inventory,
  bounded command output, and status. It never embeds the raw patch.

## Fixed Validation Profiles

`standard` executes these fixed commands inside the temporary worktree:

```text
python -m compileall -q agent_solution
python -m pytest -q
python -m ruff check agent_solution scripts
git diff --check
```

`git_diff_check` exists only as the smallest deterministic profile for narrow
integration tests.

## CLI

```powershell
python -m agent_solution validate-patch `
  --repository . `
  --patch-file .\artifacts\proposed-fix.diff `
  --base-ref HEAD `
  --profile standard `
  --artifact-dir .\artifacts
```

Use `--allow-path shipping.py` one or more times when a patch must be limited to
an explicit path set.

Use `--retain-worktree` only for manual debugging. The machine-readable result
then records the retained detached-worktree path. Without that flag, cleanup is
attempted automatically and recorded as `worktree_cleanup`.

## Status Semantics

| Status | Meaning |
|---|---|
| `VALIDATED` | Patch applied in the isolated worktree and every fixed validation command passed. |
| `PATCH_REJECTED` | Static patch-safety contract rejected the input before mutation. |
| `PATCH_APPLY_FAILED` | The patch could not cleanly apply in the isolated worktree. |
| `VALIDATION_FAILED` | Patch applied, but a fixed validation command failed or timed out. |
| `WORKTREE_CREATE_FAILED` | Detached worktree creation failed. |
| `CLEANUP_FAILED` | Validation passed but automatic temporary-worktree cleanup failed. |

A `VALIDATED` result does not itself merge, commit, push, or declare production
approval. Phase 05 owns readiness policy.
