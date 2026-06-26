# Delivery Runbook

This runbook is the final deterministic checklist for the technical challenge.
It is intentionally small enough to run under deadline pressure.

## 1. Recreate the Python environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## 2. Configure the local product runtime

Copy `.env.example` to `.env` and set only local paths:

```powershell
Copy-Item .env.example .env
```

The delivery ZIP excludes GGUF weights, `.env`, `.venv`, model caches, Node
modules, raw runtime transcripts, and benchmark harness scripts. It includes
model acquisition/runtime instructions and summarized benchmark evidence.

## 3. Run all deterministic phase tests

```powershell
.\.venv\Scripts\python.exe scripts\run_phase_validation.py --phase all
```

Or from PowerShell:

```powershell
.\scripts\run_all_phase_validation.ps1 -Phase all
```

The output identifies the failing group as `phase02`, `phase03`, `phase04`,
`phase05`, `ruff`, or `git_diff_check`.

## 4. Phase 03 live gates

Run against the local Qwen3.5 product runtime in fresh state directories:

- Gate A: `Review shipping.py.`
- Gate B: exact repeat using unchanged state/repository, expecting cache hit
- Gate C: `¿Qué hace calculate_shipping en shipping.py?`
- Gate D: review a nonexistent explicit target, expecting
  `INSUFFICIENT_EVIDENCE` and zero model calls

Do not run B/C/D if the preceding gate fails. Preserve every state directory
and report path for evidence.

## 5. Phase 04 and Phase 05 demo

1. Save an explicit unified patch proposal as `artifacts/proposed-fix.diff`.
2. Run `validate-patch` against `HEAD` in the controlled repository.
3. Pass the resulting Phase 04 JSON artifact and Phase 03 JSON analysis output
to `readiness`.
4. Show that the source checkout did not change and every validation command
ran in a detached worktree.

## 6. Final packaging check

Include source, tests, documentation, audit records, policies, example config,
and summarized model-selection evidence. Exclude secrets, model weights,
environments, caches, raw benchmark harnesses, and raw model transcripts.
