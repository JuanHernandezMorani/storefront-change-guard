# Phase-03-FIX-05 — Jinja-rendered llama-cli prompt echo boundary

## Observed live evidence

The Phase 03 diagnostic reported all of the following in one invocation:

- raw stdout began with `Loading model...`;
- raw stdout contained the `> ` prompt echo marker;
- raw stdout contained exactly one `[Start thinking]...[End thinking]` pair;
- the existing exact source-prompt matcher did not strip the wrapper;
- only the terminal performance trailer was removed.

The likely cause is that `llama-cli --jinja` echoed a chat-template-rendered prompt rather than the original prompt-file bytes. Exact source-prompt matching is therefore unavailable for this runtime path.

## Correction

The runner now has a narrowly scoped fallback that strips only when all conditions hold:

1. stdout begins with the known `Loading model...` banner;
2. stdout contains a `> ` command-prompt echo marker before the response;
3. stdout contains exactly one `[Start thinking]` marker.

It strips only up to that marker, then reuses the existing trailer stripping and strict observed-thinking-tag normalization. It does **not** locate JSON inside arbitrary prose or relax the envelope parser.

## New regression coverage

- Jinja-rendered prompt echo differs from source prompt, but a complete observed thinking block and JSON output are accepted.
- Repeated thinking markers are rejected rather than silently stripping ambiguous content.

## Required local verification

1. `python -m pytest agent_solution/tests/test_local_model_runner.py -q`
2. `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_all_phase_validation.ps1 -Phase all`
3. `./run_phase03_review_smoke.ps1`

Proceed to Gates B–D only if Gate A returns `ANALYSIS_COMPLETED` with non-empty evidence.
