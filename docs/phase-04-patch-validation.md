# Phase 04 — Isolated Patch Validation

## Purpose

Phase 04 validates a supplied unified diff without modifying the source
checkout, its branch, index, or commit history. It contains no model invocation.

```text
supplied patch
-> static safety checks
-> detached temporary Git worktree
-> git apply --check
-> git apply
-> fixed allowlisted commands
-> machine-readable validation artifact
```

## Safety contract

- The source repository is read only throughout the run.
- The patch applies only in a detached worktree created from an explicit commit.
- Every process uses an argument array; shell interpolation is forbidden.
- Arbitrary model-generated commands are forbidden.
- Binary patches, traversal, Git metadata paths, sensitive filenames,
  rename/copy patches, and oversized patches are rejected before worktree
  creation.
- Artifacts contain patch fingerprint, changed-path inventory, bounded command
  evidence, and status; they do not embed the patch body.

## Standard profile

```text
python -m compileall -q agent_solution
python -m pytest -q
python -m ruff check agent_solution scripts
git diff --check
```

## Recorded live validation

The delivered run used a controlled patch that introduced
`STANDARD_SHIPPING_CENTS` in `shipping.py` and added two behavior tests. The
patch was not applied to the source checkout.

| Field | Recorded value |
|---|---|
| Run ID | `phase04-f90b2e47f8c5` |
| Base commit | `618851b4ec4ef5787fba1caf1b08f1aa7cbd415b` |
| Status | `VALIDATED` |
| Source checkout unchanged | `true` |
| Commands | worktree create, preflight, apply, compileall, pytest, Ruff, diff check, cleanup |
| Command result | all passed with exit code `0` and no timeout |

Artifact: `artifacts/phase04-live/run-20260626-032234/phase04-f90b2e47f8c5.validation.json`.

## CLI

```powershell
python -m agent_solution validate-patch `
  --repository . `
  --patch-file .\artifacts\proposed-fix.diff `
  --base-ref HEAD `
  --profile standard `
  --artifact-dir .\artifacts
```

Use `--allow-path` to restrict a patch to an explicit path set. Use
`--retain-worktree` only for manual debugging; the retained detached path is
then recorded in the result.

`VALIDATED` does not merge, commit, push, deploy, or declare production
approval. Phase 05 owns readiness policy.
