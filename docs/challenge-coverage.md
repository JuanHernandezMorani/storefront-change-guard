# Challenge Coverage Matrix

This matrix maps the delivered prototype to the requested technical-evaluation
areas and identifies the supporting evidence.

| Evaluation area | Delivered behavior | Evidence |
|---|---|---|
| Actionable code review | The local model receives bounded repository evidence, returns structured claims/findings, and must pass deterministic schema/evidence validation. | Phase 03 Gate A; `agent_solution/analysis/`; `REPORT/executions/run-015-phase-03-live-gates.md` |
| Questions about code or documentation | File-scoped questions resolve explicit paths and can run in Spanish. | Phase 03 Gate C; `agent_solution/intake/`; `agent_solution/analysis/evidence.py` |
| Detect, propose, and validate a correction | The review identifies a hardcoded shipping rate; a supplied correction is statically checked, applied only in a detached worktree, and validated by fixed commands. | Phase 04 artifact and `scripts/run_phase04_live_validation.ps1` |
| Readiness decision | A deterministic policy consumes only Phase 03/04 JSON artifacts and returns reason-coded readiness. | Phase 05 artifact and `agent_solution/decision/policy.py` |
| Privacy and local operation | One local GGUF model; no cloud provider required; no absolute model path in result artifacts. | `docs/model-selection.md`; `agent_solution/model/` |
| Cost, latency, and operability | The design uses one local model, bounded evidence/context, no model call in Phases 04/05, and scripts for repeatable validation. | `docs/decision-document.md`; `docs/delivery-runbook.md` |
| Safety and auditability | No model shell authority, source checkout mutation, auto-merge, or readiness override; machine-readable artifacts and fixed command arrays. | `docs/architecture.md`; Phase 04/05 artifacts |
| Reproducibility | Python package, tests, example configuration, deterministic runner, and tracked operational scripts. | `pyproject.toml`; `scripts/`; `docs/delivery-runbook.md` |

## Scope statement

The prototype is intentionally not a full autonomous developer platform. It
does not include model routing, cloud inference, unrestricted terminal access,
automatic commits, merges, deployment, or broad repository indexing. Those
exclusions preserve a small, auditable demonstration surface.
