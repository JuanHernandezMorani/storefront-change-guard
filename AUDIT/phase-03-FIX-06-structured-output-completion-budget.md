# Phase-03-FIX-06 ? Structured Output Completion Budget

## Live evidence

Gate A reached the sanitized model response successfully:

- llama-cli exited with code `0`;
- deterministic CLI wrapper removal succeeded;
- observed thinking tags were normalized;
- the thinking envelope was complete;
- the final payload began as a JSON object;
- the final payload ended inside an unterminated JSON string with more opening than closing braces.

The Python capture limit was not reached. The runtime profile completion limit
was increased from `1024` to `2048` as a measured budget correction, but the
4B Q4 candidate still emitted incomplete JSON. The subsequent controlled
candidate comparison selected the 9B IQ3 runtime for the remaining live gates;
see `phase-03-FIX-07-runtime-model-identity-and-capability-selection.md`.

## Correction

- Increase the default completion limit from `1024` to `2048`.
- Increase the default timeout from `120` to `180` seconds.
- Permit an explicit `STORE_FRONT_GUARD_MODEL_COMPLETION_LIMIT` override.
- Keep one invocation, no retry, no fallback model, and the strict JSON parser.

## Acceptance criteria

1. Deterministic validation remains green.
2. The selected product candidate returns `ANALYSIS_COMPLETED` in Gate A.
3. Gate A produces non-empty evidence and valid structured output.
4. Historical sequencing condition: Gates B–D begin only after Gate A passes. Satisfied in the recorded live run.

## Closeout

The selected 9B IQ3 candidate completed Gate A and the full Gate A–D sequence.
The completion-budget change remains part of the runtime contract; no fallback
or retry path was introduced.
