# Delivery Runbook

This is the operational sequence for reproducing the demonstrated workflow on a
Windows checkout. All delivery PowerShell scripts live under `scripts/`; no
script outside that directory is required.

## 1. Bootstrap

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and set only local paths. Do not commit `.env` or
model binaries.

```powershell
Copy-Item .env.example .env
```

## 2. Deterministic validation

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\run_all_phase_validation.ps1 `
  -Phase all

git diff --check
git diff --cached --check
```

The runner covers phase-scoped tests for Phases 00, 02, 03, 04, and 05, plus
Ruff and `git diff --check`.

## 3. Phase 03 live gates

Provide the local `llama-cli` executable and one selected 9B GGUF. The default
model location is `agent_solution/model/Qwen3.5-9B-UD-IQ3_XXS.gguf`.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\run_phase03_live_gates.ps1 `
  -LlamaCli "C:\path\to\llama-cli.exe" `
  -Model ".\agent_solution\model\Qwen3.5-9B-UD-IQ3_XXS.gguf"
```

Expected sequence:

| Gate | Expected result |
|---|---|
| A | `ANALYSIS_COMPLETED`, cache miss, selected model identity |
| B | `ANALYSIS_CACHE_HIT`, cache hit, selected model identity |
| C | `ANALYSIS_COMPLETED` for the Spanish file-scoped request |
| D | `INSUFFICIENT_EVIDENCE` with no model identity |

The runner stops at the first failure and persists artifacts under
`artifacts/phase03-live/` unless `-ArtifactRoot` is supplied.

## 4. Phase 04 isolated patch validation

The delivery runner creates a controlled patch that replaces the root
`shipping.py` magic number with `STANDARD_SHIPPING_CENTS` and adds behavior
tests. It applies that patch only in a detached worktree.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\run_phase04_live_validation.ps1 `
  -Repository $PWD `
  -BaseRef HEAD
```

Expected result: `VALIDATED`, all fixed commands pass, and the source checkout
status remains unchanged. The generated artifact location is printed by the
script.

## 5. Phase 05 deterministic readiness

Use the Gate A output from Phase 03 and the validated Phase 04 artifact.

```powershell
$analysisArtifact = ".\artifacts\phase03-live\<run>\gate-a\stdout.json"
$validationArtifact = ".\artifacts\phase04-live\<run>\phase04-<id>.validation.json"

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\run_phase05_live_decision.ps1 `
  -Repository $PWD `
  -AnalysisArtifact $analysisArtifact `
  -PatchValidationArtifact $validationArtifact
```

Expected result: `READY` with policy version `phase-05.1.0`. The script
canonicalizes JSON input encoding to UTF-8 without a BOM before it invokes the
Python CLI. It does not start a model, apply a patch, execute test commands, or
change tracked source files.

## 6. Delivery-package contents

Include:

- source and tests;
- `scripts/`, documentation, audits, reports, and policies;
- selected successful machine-readable live artifacts when delivery evidence is
  required.

Exclude:

- `.git`, `.venv`, cache directories, `node_modules`, generated package
  metadata, GGUF weights, `.env`, credentials, raw model reasoning, and
  benchmark harness scripts.

The provided package contains the successful Phase 04 and Phase 05 artifacts
and concise records for Phase 03. It intentionally excludes exploratory scripts
outside `scripts/`.
