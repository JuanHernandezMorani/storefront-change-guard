# Storefront Change Guard

Local-first prototype for evidence-grounded e-commerce code review, isolated
patch validation, and deterministic readiness decisions.

## Delivery status

The implementation is organized as a bounded workflow. Language-model output is
advisory; evidence collection, patch validation, and readiness decisions remain
deterministic.

| Phase | Result | Evidence |
|---|---|---|
| Phase 00–02 | Accepted in prior audit records | `AUDIT/` and phase tests |
| Phase 03 | Live gates A–D passed with one local 9B runtime | `REPORT/executions/run-015-phase-03-live-gates.md` |
| Phase 04 | Controlled supplied patch validated in a detached worktree | `artifacts/phase04-live/run-20260626-032234/` |
| Phase 05 | Deterministic policy returned `READY` | `artifacts/phase05-live/run-20260626-033155/` |
| Phase 06 | Delivery documentation, reproducibility scripts, and package review consolidated | `AUDIT/phase-06-delivery-readiness.md` |

The recorded live model is `Qwen3.5-9B-UD-IQ3_XXS.gguf`
(`qwen3.5-9b-ud-iq3-xxs`). It is not included in source delivery.

## Demonstrated capabilities

The challenge requires at least two capabilities. This prototype demonstrates
three connected capabilities:

1. **Evidence-grounded code review** using one local model and strict structured-output validation.
2. **Bounded codebase Q&A** over explicitly requested repository files, including a Spanish request path.
3. **Correction validation and readiness evaluation**: a supplied patch is validated only in a detached worktree, then a deterministic policy evaluates the resulting artifacts.

The model does not receive shell authority, apply patches, commit, merge, push,
or decide readiness.

## Architecture

```text
request
  -> deterministic intake and bounded Git evidence
  -> one local Qwen model for advisory structured analysis
  -> deterministic schema and evidence validation
  -> supplied patch in a detached Git worktree
  -> fixed allowlisted validation commands
  -> deterministic readiness policy
```

### Trust boundaries

- **Model:** may produce analysis claims and findings only from supplied evidence.
- **Evidence validator:** rejects invalid JSON, invalid claim structure, and unsupported evidence references.
- **Patch validator:** accepts only a supplied unified diff, applies it only in a detached worktree, and executes fixed command arrays.
- **Readiness policy:** consumes prior JSON artifacts and cannot invoke a model, execute tests, or mutate the repository.

## Model selection

The selected 9B IQ3 GGUF was chosen through a controlled product-level test,
not raw throughput alone. Under the same request, evidence, runtime executable,
sanitizer, parser, and 2048-token completion budget:

| Candidate | Outcome |
|---|---|
| `Qwen3.5-4B-UD-Q4_K_XL.gguf` | Repeated strict-output failure: incomplete JSON after wrapper normalization |
| `Qwen3.5-9B-UD-IQ3_XXS.gguf` | Completed the structured analysis contract and passed all Phase 03 live gates |

The decision is intentionally narrow: it selects a single model for this
prototype and contract. It does not establish general model superiority. See
[`docs/model-selection.md`](docs/model-selection.md).

## Quick start

### 1. Create the environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 2. Configure local runtime assets

Copy `.env.example` to `.env` and set the path to the local `llama-cli`
executable. Place the selected GGUF at the documented expected path, or pass
`-Model` explicitly to the Phase 03 runner.

```powershell
Copy-Item .env.example .env
```

### 3. Run deterministic validation

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\run_all_phase_validation.ps1 `
  -Phase all
```

### 4. Run Phase 03 live gates

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\run_phase03_live_gates.ps1 `
  -LlamaCli "C:\path\to\llama-cli.exe" `
  -Model ".\agent_solution\model\Qwen3.5-9B-UD-IQ3_XXS.gguf"
```

The runner persists future gate outputs under `artifacts/phase03-live/` by
default. It validates four cases: successful review, cache reuse, Spanish
file-scoped Q&A, and insufficient evidence for a nonexistent target.

### 5. Run Phase 04 and Phase 05 live evidence

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\run_phase04_live_validation.ps1 `
  -Repository $PWD `
  -BaseRef HEAD
```

Use the resulting Phase 04 validation artifact together with Gate A's
`stdout.json` for Phase 05:

```powershell
$analysisArtifact = ".\artifacts\phase03-live\<run>\gate-a\stdout.json"
$validationArtifact = ".\artifacts\phase04-live\<run>\phase04-<id>.validation.json"

powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\scripts\run_phase05_live_decision.ps1 `
  -Repository $PWD `
  -AnalysisArtifact $analysisArtifact `
  -PatchValidationArtifact $validationArtifact
```

## Repository layout

```text
agent_solution/    Python implementation and tests
scripts/           Tracked operational runners and deterministic test wrapper
docs/              Architecture, decision, runbook, presentation, and model notes
AUDIT/             Phase-level engineering records
REPORT/            Execution summaries, change notes, and AI-use disclosure
artifacts/         Generated runtime evidence; ignored by Git, included only when packaged intentionally
policies/          Machine-readable quality policy input
demo-storefront/   Controlled storefront scenario and attribution
```

No operational `.ps1`, `.bat`, or `.sh` file is required outside `scripts/`.
The `.gitignore` enforces that policy.

## Delivery boundaries

The delivery package excludes model weights, `.env`, virtual environments,
cache directories, Git metadata, raw benchmark harnesses, and raw model
reasoning. It includes source, tests, scripts, documentation, policy files,
and selected machine-readable live artifacts.

See [`docs/delivery-runbook.md`](docs/delivery-runbook.md) for the final
execution sequence, [`docs/decision-document.md`](docs/decision-document.md)
for the concise project rationale, and
[`docs/challenge-coverage.md`](docs/challenge-coverage.md) for requirement
coverage.
