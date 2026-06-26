# Delivery Manifest

## Included

- Python source under `agent_solution/`
- Automated tests and project metadata
- PowerShell and Python operational runners under `scripts/`
- Documentation under `docs/`
- Engineering audits under `AUDIT/`
- Execution summaries and AI-use disclosure under `REPORT/`
- Policies and controlled storefront scenario
- Successful Phase 04 and Phase 05 machine-readable artifacts

## Excluded

- Git metadata and worktrees
- Virtual environments and package caches
- Local model weights and model caches
- `.env`, credentials, and secrets
- Raw model reasoning or raw model transcripts
- Benchmark harnesses and historical exploratory scripts
- Generated `*.egg-info/` metadata

## Script placement policy

The repository ignores `.ps1`, `.bat`, and `.sh` files by default and only
allows tracked operational scripts under `scripts/`. Required delivery scripts:

- `scripts/run_all_phase_validation.ps1`
- `scripts/run_phase03_live_gates.ps1`
- `scripts/run_phase04_live_validation.ps1`
- `scripts/run_phase05_live_decision.ps1`

No script outside `scripts/` is required for the delivered workflow.
