# Local Model Runtime

## Product model policy

Storefront Change Guard runs **one local model per product process**. It does
not use fallback models, routing, cloud inference, or multi-agent execution.

The selected Phase 03 candidate is:

```text
Qwen3.5-9B-UD-IQ3_XXS.gguf
runtime ID: qwen3.5-9b-ud-iq3-xxs
runtime: llama.cpp / llama-cli
```

The selection changed after a controlled product Gate A comparison: the prior
4B Q4 candidate was faster in the broad benchmark but repeatedly returned
incomplete JSON under the product's strict structured-output contract; the 9B
IQ3 candidate completed Gate A successfully. The full rationale and evidence
boundary are in [`model-selection.md`](model-selection.md).

## Runtime boundary

```text
bounded repository evidence
→ one llama-cli invocation
→ deterministic stdout sanitizer
→ optional thinking-envelope discard
→ strict JSON parser and schema validation
→ structured result
```

The model is advisory. Evidence validation, patch isolation, command execution,
and readiness policy remain deterministic.

## Configuration

Copy `.env.example` to `.env` and set local paths only:

```powershell
Copy-Item .env.example .env
```

Required:

```text
STORE_FRONT_GUARD_LLAMA_EXECUTABLE
```

Optional explicit model path:

```text
STORE_FRONT_GUARD_MODEL_PATH
```

The default expects the selected 9B IQ3 GGUF under
`agent_solution/model/`. An explicit path is useful for a controlled
verification run. It replaces the single active model for that process and is
not a fallback mechanism.

The runtime artifact persists only a derived `model_id` and `model_filename`;
it never emits the absolute local model path.

## Production profile

```text
--jinja
-st
-f <temporary prompt file>
--no-display-prompt
stdin = DEVNULL
context = 8192
completion limit = 2048
temperature = 0.0
top-p = 1.0
min-p = 0.1
repeat penalty = 1.0
flash attention = on
```

The completion budget was increased after live evidence showed that a 1024-token
budget could end inside the required JSON response. The strict parser was not
relaxed and the product still performs one model invocation only.

## Current live validation status

- Gate A: passed with the 9B IQ3 candidate; the final rerun must record the
  corrected dynamic model identity.
- Gate B: pending cache-hit validation.
- Gate C: pending Spanish codebase-question validation.
- Gate D: pending nonexistent-target / zero-model-call validation.

## Privacy

- Repository evidence stays local by default.
- Raw model reasoning is discarded immediately after envelope extraction.
- Raw runtime transcripts and model weights are excluded from delivery.
- Model paths, `.env`, and secrets are not committed.
