# Execution Report — Run 009: Phase-03 Validation 01 Live Single-Model Runtime

## Execution Metadata

| Item | Value |
|---|---|
| Run ID | `run-009` |
| Phase | Phase-03 Validation 01 |
| Purpose | Live single-model runtime validation |
| Date | 2026-06-24 |
| Model | `Qwen3.5-4B-UD-Q4_K_XL.gguf` |
| Runtime | `llama.cpp` v791 |
| Repository SHA | `275bb5400b564d69b4b8d0ebc3d0b5fb81936110` |

## Execution Summary

| Step | Status | Notes |
|---|---|---|
| Preflight verification | PASS | Git state, model, CLI all verified |
| Runtime config capture | PASS | Single-model config confirmed |
| Smoke 1: English code review | FAIL | llama-cli enters interactive mode |
| Smoke 2: Cache hit | BLOCKED | Dependent on Smoke 1 |
| Smoke 3: Spanish question | BLOCKED | Dependent on Smoke 1 |
| Smoke 4: Model unavailable | PASS (unit) | Validated via existing tests |
| Smoke 5: Invalid output | PASS (unit) | Validated via existing tests |
| Smoke 6: Prompt injection | PASS (unit) | Validated via existing tests |
| Final validation commands | PASS | All 12 commands pass |
| Repository integrity | PASS | No unauthorized modifications |

## Detailed Findings

### Critical Defect: llama-cli Interactive Mode

**Location:** `agent_solution/model/runner.py` — `_build_command()` and `run_model()`

**Symptom:** When `llama-cli` is invoked with a prompt (`-p`) for a model that has a chat template (Qwen3.5-4B), it automatically enters interactive conversation mode. The process hangs indefinitely waiting for user input, never producing completion output.

**Evidence:**
```
llama-cli.exe: chat template is available, enabling conversation mode
llama-cli.exe: interactive mode on.
```

**Expected behavior:** Single-turn completion mode that produces output and exits.

**Actual behavior:** Interactive conversation mode that waits for input.

**Root cause:** `llama-cli` is the interactive chat tool. For non-interactive single-turn completion, `llama-completion` should be used.

**Verified flags:**
- `-no-cnv` / `--no-conversation` — NOT supported by `llama-cli` (returns error)
- `-st` / `--single-turn` — Does not prevent interactive mode with `-p` and chat template

**Impact:** All live model smoke tests (Smoke 1, 2, 3) fail. Unit tests pass because they do not invoke the actual model.

### Non-Blocking: flash-attn Flag Format

**Location:** `agent_solution/model/runner.py:47`

**Finding:** The runner passes `--flash-attn` as a bare flag, but llama-cli v791 expects `--flash-attn [on|off|auto]`.

**Impact:** Low — flash_attention_enabled defaults to False, so this flag is not currently added to the command. Would fail if enabled.

## Safe Command Metadata (Attempted)

| Field | Value |
|---|---|
| Runtime backend | llama.cpp |
| Effective model ID | qwen3.5-4b-ud-q4-k-xl |
| Effective model filename | Qwen3.5-4B-UD-Q4_K_XL.gguf |
| Context limit | 4096 |
| Completion limit | 1024 |
| Timeout | 120s |
| Confirmed CLI flags | -m, -c, -n, -t, -b, -ub, --temp, --top-p, --min-p, --repeat-penalty, --no-display-prompt, -p, --cache-type-k, --cache-type-v |
| Command completed | No (hung in interactive mode) |
| Exit code | N/A |
| Elapsed wall-clock | N/A (timed out) |
| Safe stdout bytes | 0 |
| Safe stderr bytes | 0 |

## Outcome

**CHANGES_REQUIRED** — The `LocalModelRunner` must be updated to use `llama-completion` instead of `llama-cli` for non-interactive single-turn completion, or a mechanism must be added to prevent `llama-cli` from entering interactive mode.
