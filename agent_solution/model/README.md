# Model Directory

This directory holds lightweight runtime metadata only. GGUF weights are ignored
by Git and excluded from the delivery package.

## Selected runtime

- **Model:** `Qwen3.5-9B-UD-IQ3_XXS.gguf`
- **Runtime ID:** `qwen3.5-9b-ud-iq3-xxs`
- **Runtime:** local llama.cpp `llama-cli`
- **Selection basis:** the 9B IQ3 candidate completed the strict Phase 03
  structured-output contract and recorded Gates A–D; the compared 4B Q4
  candidate repeatedly produced incomplete JSON under the same Gate A contract.

The runtime remains one-model only. An explicit
`STORE_FRONT_GUARD_MODEL_PATH` replaces the active model for that process; it
is not a fallback, retry, or routing mechanism.

## Expected location

```text
agent_solution/model/Qwen3.5-9B-UD-IQ3_XXS.gguf
```

A different local path can be supplied without exposing it in result artifacts:

```text
STORE_FRONT_GUARD_MODEL_PATH=C:\local-models\Qwen3.5-9B-UD-IQ3_XXS.gguf
```

## Runtime configuration

```text
STORE_FRONT_GUARD_LLAMA_EXECUTABLE        # required: local llama-cli executable
STORE_FRONT_GUARD_MODEL_PATH              # optional GGUF override
STORE_FRONT_GUARD_MODEL_COMPLETION_LIMIT  # default: 2048
STORE_FRONT_GUARD_MODEL_TIMEOUT           # default: 180 seconds
STORE_FRONT_GUARD_MODEL_THREADS           # default: 12
```

The runner uses one local invocation with `--jinja`, `-st`, `-f`, and
`--no-display-prompt`, with stdin disconnected. Raw reasoning is not retained.

See `../../docs/model-selection.md` for scope and recorded evidence.
