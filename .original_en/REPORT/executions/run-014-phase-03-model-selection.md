# Run 014 — Phase 03 Model Selection Evidence

## Purpose

Record the model-selection correction made after the real Phase 03 Gate A
structured-output runtime test.

## Controlled comparison

The compared product runs held the following constant:

- repository and explicit target: `shipping.py`;
- request: `Review shipping.py.`;
- one local `llama-cli` invocation;
- evidence collection and strict validation pipeline;
- deterministic stdout sanitizer;
- 2048-token completion budget;
- no fallback, retry, routing, or cloud model.

The candidate GGUF changed.

| Candidate | Result |
|---|---|
| `Qwen3.5-4B-UD-Q4_K_XL.gguf` | Repeated `MODEL_OUTPUT_INVALID` results due to incomplete JSON (`MALFORMED_JSON_NO_CLOSING_BRACE`) after the CLI wrapper was sanitized |
| `Qwen3.5-9B-UD-IQ3_XXS.gguf` | `ANALYSIS_COMPLETED`, exit code `0`, non-empty evidence, and a schema-valid grounded result |

## Decision

Use `Qwen3.5-9B-UD-IQ3_XXS.gguf` as the single active product model for the
remaining Phase 03 live gates. The result artifact must identify the actual
active GGUF filename and its derived ID.

## Limits of this record

- The broad benchmark established speed and host RSS; it did not score
  semantic quality automatically.
- One Gate A pass is not a general quality claim.
- Gate B cache behavior, Gate C Spanish Q&A, and Gate D insufficient-evidence
  behavior remain required before Phase 03 closure.
- This report deliberately excludes raw model reasoning and raw runtime
  transcript content.

## Related records

- `docs/model-selection.md`
- `AUDIT/phase-03-FIX-07-runtime-model-identity-and-capability-selection.md`
- `docs/model-selection.md`
