# Phase-03-FIX-06 ? Structured Output Completion Budget

## Live evidence

Gate A reached the sanitized model response successfully:

- llama-cli exited with code `0`;
- deterministic CLI wrapper removal succeeded;
- observed thinking tags were normalized;
- the thinking envelope was complete;
- the final payload began as a JSON object;
- the final payload ended inside an unterminated JSON string with more opening than closing braces.

The Python capture limit was not reached. The runtime profile completion limit was
`1024`, which was insufficient for reasoning plus the required structured JSON
schema.

## Correction

- Increase the default completion limit from `1024` to `2048`.
- Increase the default timeout from `120` to `180` seconds.
- Permit an explicit `STORE_FRONT_GUARD_MODEL_COMPLETION_LIMIT` override.
- Keep one invocation, no retry, no fallback model, and the strict JSON parser.

## Acceptance criteria

1. Deterministic validation remains green.
2. Gate A returns `ANALYSIS_COMPLETED`.
3. Gate A produces non-empty evidence and valid structured output.
4. Gates B-D remain blocked until Gate A passes.
