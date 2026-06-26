# Decision Log

| ID | Date | Decision | Status |
|---|---|---|---|
| D-001 | 2026-06-23 | Use a local-first model interface rather than requiring a hosted provider. | Accepted |
| D-002 | 2026-06-23 | Prioritize operability, privacy, response time, then cost. | Accepted |
| D-003 | 2026-06-23 | Focus on evidence-grounded review and isolated correction validation; integrate readiness as a bounded policy layer. | Accepted |
| D-004 | 2026-06-23 | Keep the source checkout immutable during patch validation; use temporary detached Git worktrees. | Accepted |
| D-005 | 2026-06-23 | Make deterministic evidence, command outcomes, and policy gates authoritative; keep model output advisory. | Accepted |
| D-006 | 2026-06-26 | Select `Qwen3.5-9B-UD-IQ3_XXS.gguf` as the one Phase 03 product model after a controlled structured-output comparison. | Accepted |
| D-007 | 2026-06-26 | Keep Phase 04 and Phase 05 operational runners in `scripts/`; exclude root-level exploratory scripts from delivery. | Accepted |

## D-006 — Capability-based single-model selection

- **Decision:** Use `Qwen3.5-9B-UD-IQ3_XXS.gguf` and derive runtime identity
  from its active filename.
- **Context:** The 4B Q4 candidate was faster in broad measurements but
  repeatedly produced incomplete JSON under the actual strict Phase 03
  contract. The 9B IQ3 candidate completed Gate A and the subsequent live gates.
- **Alternatives rejected:** Relaxing the parser, adding a fallback or retry
  model, introducing routing, or using cloud inference.
- **Consequences:** Higher local resource use than 4B candidates in exchange
  for demonstrated structured-output completion for this contract.
- **Evidence:** `docs/model-selection.md` and
  `REPORT/executions/run-015-phase-03-live-gates.md`.

## D-007 — Tracked operational script boundary

- **Decision:** Delivery scripts are stored only under `scripts/`.
- **Context:** The Git ignore policy excludes shell and PowerShell files outside
  that directory. Earlier exploratory root-level scripts are not required for
  the delivered workflow.
- **Consequences:** A fresh checkout has all necessary operational runners in a
  trackable location, while ad hoc diagnostics do not become delivery
  dependencies.
- **Evidence:** `docs/delivery-manifest.md` and `.gitignore`.
