# Storefront Change Guard — Decision Document

## Problem and selected scope

Storefront Change Guard is a local-first prototype for e-commerce engineering
workflows. It demonstrates three bounded capabilities:

1. evidence-grounded code review;
2. validation of a supplied correction in an isolated Git worktree; and
3. deterministic readiness evaluation from prior machine-readable artifacts.

The first two satisfy the primary challenge scope. The readiness policy provides
an additional controlled decision layer.

## Architecture and authority model

```text
intake + Git evidence
-> one local structured analysis
-> deterministic evidence validation
-> supplied patch in detached worktree
-> fixed validation commands
-> deterministic readiness policy
```

The local model is advisory. It cannot run shell commands, apply a patch, alter
the source checkout, commit, merge, push, or override quality gates. The source
checkout stays unchanged during Phase 04 and Phase 05 live runs.

## Recorded live evidence

| Capability | Recorded result |
|---|---|
| Phase 03 review | Gate A returned `ANALYSIS_COMPLETED` with `qwen3.5-9b-ud-iq3-xxs`. |
| Cache behavior | Gate B returned `ANALYSIS_CACHE_HIT` for the identical request and state. |
| Spanish Q&A | Gate C accepted a file-scoped Spanish request and returned `ANALYSIS_COMPLETED`. |
| Safe insufficiency | Gate D returned `INSUFFICIENT_EVIDENCE` for a nonexistent explicit target. |
| Patch validation | Phase 04 returned `VALIDATED`; worktree creation, preflight, apply, compile, tests, lint, diff check, and cleanup passed. |
| Readiness | Phase 05 returned `READY` under policy `phase-05.1.0`; it made no model invocation. |

The Phase 03 model selection was empirical. The 4B Q4 candidate was faster and
lighter in broad benchmarking but repeatedly produced incomplete JSON under the
actual strict output contract. The selected 9B IQ3 candidate completed the same
contract and passed the recorded live gates. This is a project-specific
capability decision, not a broad benchmark claim.

## Trade-offs

### Cost and privacy

The product path uses one local GGUF and no hosted inference provider. Source
evidence remains local. Model weights are excluded from the delivery package.

### Latency and operability

Local inference is slower than some hosted alternatives. The design therefore
bounds file scope, context size, model calls, and output validation. Phase 04
and Phase 05 require no model call.

### Safety and autonomy

The design rejects unrestricted automation. A correction must be supplied as a
unified diff, validates only in a detached worktree, and is never merged by the
prototype. Readiness means that the recorded gates passed; it is not merge or
production authority.

## Alternatives not selected

- Cloud-only inference: weaker privacy and recurring external dependency.
- Multi-model routing, fallback, or retry chains: additional complexity without
  evidence that it improves the focused demo.
- Model-generated shell commands: unnecessary command-injection and mutation
  risk.
- Automatic merge after validation: outside the prototype's authority boundary.

## Delivery evidence

- `docs/model-selection.md`
- `REPORT/executions/run-015-phase-03-live-gates.md`
- `artifacts/phase04-live/run-20260626-032234/`
- `artifacts/phase05-live/run-20260626-033155/`
- `AUDIT/phase-06-delivery-readiness.md`

## AI assistance disclosure

AI tools assisted with exploration, drafting, implementation support, test
design, and review. The author retained ownership of the scope, architecture,
trust boundaries, acceptance criteria, runtime execution, debugging, and final
delivery decision.
