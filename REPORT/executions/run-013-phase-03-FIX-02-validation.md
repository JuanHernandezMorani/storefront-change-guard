# Execution Report — Run 013: Phase-03-FIX-02 Validation

## Execution Metadata

| Item | Value |
|---|---|
| Run ID | `run-013` |
| Phase | Phase-03-FIX-02 |
| Purpose | Test 1 Runtime Reconciliation, Structured Output Reliability, Bounded Codebase Q&A |
| Date | 2026-06-25 |
| Model | `Qwen3.5-4B-UD-Q4_K_XL.gguf` (target product model) |
| Runtime | `llama-cli` (reconciled with Test 1 profile) |
| Development Model | `Qwen3.6 35B A3B UD IQ3_XXS MTP` (not the target model) |

## Execution Summary

| Step | Status | Notes |
|---|---|---|
| Repository audit | PASS | SHA, branch, modified files captured |
| Test 1 profile reconciliation | PASS | llama-cli with --jinja, -st, -f, --no-display-prompt |
| Reasoning envelope parser | IMPLEMENTED | extract_reasoning_envelope() in orchestrator.py |
| Context budget with reasoning reservation | IMPLEMENTED | reasoning_reservation=512, final_json_reservation=max(512, completion_limit) |
| Bounded codebase evidence acquisition | IMPLEMENTED | Full repo scan for CODEBASE_QUESTION |
| Deterministic test suite | PASS | 129/129 tests passed |
| Linter | PASS | ruff check agent_solution — all checks passed |
| CLI help | PASS | Both --help and analyze --help |
| Git diff check | PASS | No whitespace errors |
| Git ignore | PASS | GGUF files properly ignored |
| Live smoke tests | PENDING | A-G require actual model execution |

## Deterministic Test Results

| Test Suite | Collected | Passed | Status |
|---|---|---|---|
| `test_intake.py` | 28 | 28 | PASS |
| `test_git_context.py` | 31 | 31 | PASS |
| `test_grounded_analysis.py` | 47 | 47 | PASS |
| `test_local_model_runner.py` | 23 | 23 | PASS |
| **Total** | **129** | **129** | **PASS** |

## Key Implementation Changes

### Runtime Selection

| Attribute | Before (FIX-01) | After (FIX-02) |
|---|---|---|
| Executable | `llama-completion` | `llama-cli` |
| Non-interactive flag | `-no-cnv` | `-st` |
| Chat template | Not present | `--jinja` (explicit) |
| Reasoning handling | None | `extract_reasoning_envelope()` |

### Reasoning Envelope

- Shape A: Plain JSON with optional whitespace
- Shape B: `<think>` + reasoning + `</think>` + JSON
- Reasoning discarded immediately after extraction
- Never cached, stored, rendered, or used as evidence

### Context Budget

```
reasoning_reservation = 512
final_json_reservation = max(512, completion_limit)
configured_generation_limit = reasoning_reservation + final_json_reservation
estimated_prompt_tokens = ceil(prompt_utf8_bytes / 2)
reserved_generation_margin = max(128, ceil(completion_limit * 0.10))
```

### Bounded Evidence

- Full repository scan for `CODEBASE_QUESTION` (not just changed files)
- Max 500 files inventory
- Max 3 search queries
- Max 8 evidence records
- No embeddings, no semantic retrieval, no shell execution

## Files Modified

1. `agent_solution/analysis/models.py` — Added `ModelEnvelopeDiagnostics` dataclass
2. `agent_solution/analysis/orchestrator.py` — Added `extract_reasoning_envelope()`, reasoning-aware context budget
3. `agent_solution/model/config.py` — Updated default executable to `llama-cli`
4. `agent_solution/model/runner.py` — Complete rewrite for llama-cli Test 1 profile
5. `agent_solution/tests/test_local_model_runner.py` — Updated all fixtures to `llama-cli`
6. `agent_solution/tests/test_grounded_analysis.py` — Updated all fixtures to `llama-cli`
7. `.env.example` — Updated environment variable reference

## Validation Commands

| Command | Status |
|---|---|
| `python -m compileall -q agent_solution` | PASS |
| `python -m pytest agent_solution/tests/test_intake.py -v` | PASS (28/28) |
| `python -m pytest agent_solution/tests/test_git_context.py -v` | PASS (31/31) |
| `python -m pytest agent_solution/tests/test_grounded_analysis.py -v` | PASS (47/47) |
| `python -m pytest agent_solution/tests/test_local_model_runner.py -v` | PASS (23/23) |
| `python -m ruff check agent_solution` | PASS |
| `python -m agent_solution --help` | PASS |
| `python -m agent_solution analyze --help` | PASS |
| `git diff --check` | PASS |
| `git diff --cached --check` | PASS |
| `git check-ignore -v agent_solution/model/*.gguf` | PASS |

## Live Smoke Tests Pending

The following require actual Qwen3.5-4B-UD-Q4_K_XL.gguf execution:

- **Smoke A**: llama-cli produces valid JSON output with Test 1 profile
- **Smoke B**: Cache hit for identical request (zero model invocation)
- **Smoke C**: Spanish codebase question with bounded evidence
- **Smoke D**: Prompt injection resistance
- **Smoke E**: Controlled failure — MODEL_UNAVAILABLE
- **Smoke F**: Controlled failure — MODEL_TIMEOUT
- **Smoke G**: Controlled failure — MODEL_OUTPUT_INVALID

## Explicit Statement

Phase 3 remains pending independent review. This fix does not mark Phase 3 as accepted.

No benchmark, Test 1, Test 2, model binary, or Phase 1/2 accepted artifact was modified.
