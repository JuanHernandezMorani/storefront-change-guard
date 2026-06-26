# Architecture

## Purpose

Storefront Change Guard reviews a bounded code request, validates evidence-bound
analysis, validates a supplied patch in an isolated worktree, and produces a
deterministic readiness decision.

```text
request
  -> deterministic intake and bounded Git context
  -> one local model analysis
  -> schema and evidence validation
  -> supplied patch in detached worktree
  -> fixed validation command profile
  -> deterministic readiness policy
```

## Components and trust levels

| Component | Responsibility | Authority |
|---|---|---|
| Intake | Classifies a request and resolves a bounded scope. | Deterministic |
| Git context | Collects read-only repository evidence and fingerprints. | Deterministic |
| Local model runner | Executes one local `llama-cli` invocation for structured analysis. | Advisory |
| Evidence/output validator | Validates result shape, claim policy, and evidence references. | Deterministic |
| Analysis cache | Reuses valid analysis for matching eligible scope/fingerprint state. | Deterministic |
| Patch validator | Applies a supplied diff only in a detached worktree and runs fixed commands. | Deterministic |
| Readiness policy | Evaluates only Phase 03 and Phase 04 artifacts. | Deterministic |
| Artifact writer | Emits bounded JSON evidence for later review. | Deterministic |

## Authority boundaries

- The model cannot execute shell commands or choose validation commands.
- The source checkout is not automatically modified, committed, merged, or
  pushed.
- A model finding is not proof by itself; claims must reference collected
  evidence and pass deterministic validation.
- Phase 04 accepts a supplied patch. It does not generate, merge, or deploy one.
- Phase 05 consumes artifacts only. It cannot call a model, apply a patch, run a
  test, or override failed validation.

## Non-goals

- Autonomous commits, merges, pushes, or deployment.
- Model-generated arbitrary shell commands.
- Cloud-only inference dependency.
- Multi-model routing or fallback chains.
- Vector-database indexing or broad autonomous repository exploration.
- A web user interface.

## Operational trade-off

The design favors a small, auditable workflow over broader autonomy. Bounded
context and strict validation can produce `INSUFFICIENT_EVIDENCE` for requests
outside the selected scope; that behavior is intentional.
