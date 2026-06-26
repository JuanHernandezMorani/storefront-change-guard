# Implementation Decision Notes

| Date | ID | Decision / Change | Evidence | Follow-up |
|---|---|---|---|---|
| 2026-06-23 | NOTE-001 | Created repository scaffolding and traceability conventions. | Initial kit | Complete baseline audit. |
| 2026-06-26 | NOTE-002 | Selected the one local 9B IQ3 runtime after controlled structured-output evidence; the 4B Q4 candidate did not complete this strict contract. | `run-014`, `run-015`, `docs/model-selection.md` | Retain no fallback or routing path. |
| 2026-06-26 | NOTE-003 | Consolidated required operational PowerShell runners under `scripts/`; excluded exploratory root-level scripts from delivery. | `docs/delivery-manifest.md`, `run-018` | Preserve script-placement policy. |
