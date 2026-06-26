# Phase-03-FIX-07 — Runtime Model Identity and Capability-Based Selection

## Status

Accepted. The selected 9B IQ3 model completed the recorded Phase 03 live gate
sequence A–D.

## Trigger

A controlled Gate A comparison established two facts:

1. The 4B Q4 candidate repeatedly produced incomplete JSON after the
   deterministic runtime wrapper and envelope boundary were working.
2. The 9B IQ3 candidate completed the same structured-output contract, but an
   early artifact incorrectly reported a hardcoded 4B identity.

## Correction

- Select `Qwen3.5-9B-UD-IQ3_XXS.gguf` as the one product model.
- Derive `model_filename` and `model_id` from the active GGUF filename.
- Do not include absolute model paths in analysis artifacts.
- Keep one-model operation: no fallback, routing, retry model, or cloud path.

## Live evidence

| Gate | Result |
|---|---|
| A — `Review shipping.py.` | `ANALYSIS_COMPLETED`, selected 9B identity |
| B — exact repeat | `ANALYSIS_CACHE_HIT`, selected 9B identity |
| C — Spanish file-scoped Q&A | `ANALYSIS_COMPLETED`, selected 9B identity |
| D — nonexistent explicit target | `INSUFFICIENT_EVIDENCE`, no runtime model identity |

## Scope of conclusion

The selection is based on local performance measurements plus a product-level
structured-output comparison. It is not a claim of universal model superiority.
It establishes that the selected 9B IQ3 candidate completed this project's
Phase 03 contract where the compared 4B Q4 candidate did not.

## Related records

- `docs/model-selection.md`
- `REPORT/executions/run-014-phase-03-model-selection.md`
- `REPORT/executions/run-015-phase-03-live-gates.md`
