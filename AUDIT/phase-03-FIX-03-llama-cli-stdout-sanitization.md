# Phase-03-FIX-03 — Deterministic llama-cli stdout sanitization

## Status

Implementation complete and deterministic tests added. Local runtime gates remain
pending because they require the target Windows executable and GGUF model.

## Trigger

The local live Gate A exposed deterministic `llama-cli` wrapper content on
stdout before the model response: banner text, an exact prompt echo, and a
performance/exiting trailer. The model also emitted a leading
`[Start thinking]...[End thinking]` pair rather than the strict
`<think>...</think>` spelling expected by Phase 03.

## Correction

`agent_solution/model/runner.py` now sanitizes only the observed deterministic
CLI wrapper before Phase 03 envelope parsing:

1. Banner/prompt text is removed only when the exact prompt sent by the runner
   appears after the known `Loading model...` wrapper.
2. The terminal `[ Prompt: ... ]` plus `Exiting...` trailer is removed only at
   the output end.
3. Exactly one complete leading observed thinking pair is normalized to the
   strict `<think>...</think>` form.
4. Arbitrary prose, incomplete tags, repeated tags, and unrecognized wrappers
   remain untouched so the strict envelope parser rejects them.

Raw stdout stays transient in the runner. Result/cache/session/report contracts
receive sanitized model content and compact sanitization categories only.

## Deterministic validation

The runner test suite covers known wrapper stripping, trailer stripping,
thinking-tag normalization, strict rejection of arbitrary prose, and rejection
of incomplete/repeated observed thinking tags.

## Required live follow-up

Retry only Gate A in a fresh state directory. Proceed to Gates B–D only after
Gate A produces schema-valid `ANALYSIS_COMPLETED` with non-empty evidence.
