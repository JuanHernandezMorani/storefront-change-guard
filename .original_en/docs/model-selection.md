# Model Selection — Phase 03 Structured Output Runtime

## Decision

**Selected single-model runtime:** `Qwen3.5-9B-UD-IQ3_XXS.gguf`
**Runtime ID:** `qwen3.5-9b-ud-iq3-xxs`
**Decision status:** Accepted for the delivered Phase 03 contract.

The selected model is a single local runtime choice. There is no fallback
model, routing layer, repair model, cloud model, or multi-agent path.

## Why the 9B IQ3 candidate was selected

A broad local benchmark measured speed and host memory, but it did not measure
whether a candidate could satisfy the product's strict evidence-grounded JSON
contract. A second, controlled product test therefore held the repository,
request (`Review shipping.py.`), evidence bundle, `llama-cli` executable,
sanitizer, parser, prompt schema, and 2048-token completion budget constant.
Only the GGUF candidate changed.

| Candidate | Structured-output result | Decision |
|---|---|---|
| `Qwen3.5-4B-UD-Q4_K_XL.gguf` | Repeated `MODEL_OUTPUT_INVALID` with `MALFORMED_JSON_NO_CLOSING_BRACE` after runtime wrapper normalization | Rejected for this contract |
| `Qwen3.5-9B-UD-IQ3_XXS.gguf` | `ANALYSIS_COMPLETED` with non-empty evidence and schema-valid claims/findings | Selected |

The 9B IQ3 candidate is slower and heavier than the 4B candidates measured in
the broad benchmark. The delivery requires valid, evidence-grounded structured
output; raw throughput alone is insufficient for that requirement.

## Recorded live gate results

The selected candidate completed the following Phase 03 run:

| Gate | Request class | Result |
|---|---|---|
| A | English code review of `shipping.py` | `ANALYSIS_COMPLETED`, cache miss |
| B | Identical repeat with unchanged state | `ANALYSIS_CACHE_HIT`, cache hit |
| C | Spanish file-scoped codebase question | `ANALYSIS_COMPLETED` |
| D | Nonexistent explicit file | `INSUFFICIENT_EVIDENCE`; no runtime model identity emitted |

The live gate runner validates the expected `model_id` for model-using gates,
and stores future outputs under `artifacts/phase03-live/` by default.

## Traceability

Runtime identity is derived from the active GGUF filename:

- `model_filename` is the filename only;
- `model_id` is derived from that filename;
- absolute local model paths are not included in result artifacts.

## Scope of the conclusion

This decision is deliberately narrow. It shows that the 9B IQ3 candidate passed
this project's Phase 03 structured-output contract on the target local runtime.
It does not claim that the model is universally superior, nor that one live run
is a comprehensive quality benchmark.

## Related records

- `REPORT/executions/run-014-phase-03-model-selection.md`
- `REPORT/executions/run-015-phase-03-live-gates.md`
- `AUDIT/phase-03-FIX-07-runtime-model-identity-and-capability-selection.md`
- `agent_solution/model/README.md`
