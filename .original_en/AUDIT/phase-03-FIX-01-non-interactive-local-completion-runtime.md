# Phase-03-FIX-01 — Non-Interactive Local Completion Runtime

## Fix Scope and Purpose

This fix addresses the Phase 3 local-runtime defect where `llama-cli` enters interactive conversation mode instead of producing one bounded completion. The fix replaces `llama-cli` with `llama-completion` as the configured single-turn local completion executable.

## Root Cause

The current `LocalModelRunner` invokes `llama-cli`. For the selected Qwen model with a chat template, the installed `llama-cli` enters interactive conversation mode under the current invocation pattern. The following approaches were verified as unsuitable:
- `-no-cnv` is not supported by the installed `llama-cli` executable.
- `-st` does not reliably prevent interactive conversation mode when used with `-p`.
- The current runtime path therefore hangs instead of producing one bounded completion.

## Why llama-cli Was Unsuitable

The installed `llama-cli` executable (version 791) lacks the `-no-cnv` flag required for non-interactive completion. When invoked with `-p` for the Qwen model with a chat template, it automatically enters interactive conversation mode, causing the process to hang waiting for human terminal input.

## Why llama-completion Is the Selected Runtime

The installed `llama-completion` executable supports:
- `-no-cnv` / `--no-conversation` flag for non-interactive completion
- `-f` for file-based prompt transport
- All required sampling and context flags
- Non-interactive single-turn completion behavior

## Configuration Migration

Replaced misleading `llama-cli` naming with generic executable contract:
- `STORE_FRONT_GUARD_LLAMA_CLI` → `STORE_FRONT_GUARD_LLAMA_EXECUTABLE`
- `llama_cli_path` → `runtime_executable_path`
- Added `runtime_executable_name` field

Removed hardcoded path auto-discovery. User must provide explicit executable path.

## Confirmed Completion Flags

From actual `llama-completion --help` output:
- `-m` model path
- `-c` context limit
- `-n` completion limit (tokens to predict)
- `-t` threads
- `-b` batch size
- `-ub` micro-batch size
- `--temp` temperature
- `--top-p` top-p sampling
- `--min-p` min-p sampling
- `--repeat-penalty` repeat penalty
- `--no-display-prompt` suppress prompt echo
- `-f` prompt file input
- `-no-cnv` non-interactive mode
- `--flash-attn` flash attention
- `-ctk` KV cache type K
- `-ctv` KV cache type V

## Safe Prompt Transport Choice

Uses temporary prompt file (`-f` flag) instead of `-p` argument:
- Preserves UTF-8 (English and Spanish characters)
- Avoids shell quoting issues
- Avoids raw prompt logging
- Cleans temporary files after execution
- Remains bounded by configured limits

## Timeout and Process-Cleanup Behavior

- Uses `subprocess.Popen` with explicit timeout
- On timeout, kills the child process safely
- Uses `process.kill()` and `process.wait(timeout=5)` for cleanup
- Targets only the launched process (no broad process-name termination)
- No orphan processes remain
- No unrelated processes affected

## Test Changes

Updated 19 test cases in `test_local_model_runner.py`:
- Configuration tests verify generic runtime executable fields
- Command building tests verify `-no-cnv` and `-f` flags
- Execution tests verify single process creation
- Safety tests verify no retry and no fallback behavior

Updated 47 test cases in `test_grounded_analysis.py`:
- Replaced all `llama_cli_path` references with `runtime_executable_path`
- Replaced all `llama-cli` references with `llama-completion`

## Validation Command Outcomes

- `python -m compileall -q agent_solution` — PASS
- `python -m pytest agent_solution/tests/test_intake.py -v` — PASS (28/28)
- `python -m pytest agent_solution/tests/test_git_context.py -v` — PASS (31/31)
- `python -m pytest agent_solution/tests/test_grounded_analysis.py -v` — PASS (47/47)
- `python -m pytest agent_solution/tests/test_local_model_runner.py -v` — PASS (19/19)
- `python -m ruff check agent_solution` — PASS
- `python -m agent_solution --help` — PASS
- `python -m agent_solution analyze --help` — PASS
- `git diff --check` — PASS
- `git diff --cached --check` — PASS
- `git check-ignore -v agent_solution/model/Qwen3.5-4B-UD-Q4_K_XL.gguf` — PASS

## Live Smoke Outcomes

Pending live validation (Smoke A-G).

## Project Integrity Before/After Comparison

Before fix:
```
M .env.example
M .gitignore
M AUDIT/change-register.md
M CHANGELOG.md
M agent_solution/cli.py
M agent_solution/git_tools/collector.py
M agent_solution/git_tools/excerpts.py
M agent_solution/git_tools/fingerprint.py
M agent_solution/git_tools/models.py
M pyproject.toml
?? AUDIT/phase-03-grounded-analysis-single-local-model.md
?? AUDIT/phase-03-validation-01-live-single-model-runtime.md
?? REPORT/executions/run-008-phase-03-validation.md
?? REPORT/executions/run-009-phase-03-validation-01-live-runtime.md
?? REPORT/prompts/prompt-008-phase-03-grounded-analysis-single-local-model.md
?? REPORT/prompts/prompt-009-phase-03-validation-01-live-single-model-runtime.md
?? agent_solution/analysis/
?? agent_solution/docs/
?? agent_solution/model/
?? agent_solution/tests/test_grounded_analysis.py
?? agent_solution/tests/test_local_model_runner.py
```

After fix: Additional modifications to:
- `agent_solution/analysis/models.py`
- `agent_solution/model/config.py`
- `agent_solution/model/runner.py`
- `agent_solution/model/README.md`

## Remaining Limitations

1. Live smoke tests (A-G) require actual model execution and are pending.
2. The fix only addresses the local runtime defect; other Phase 3 components remain unchanged.
3. The model binary is not tracked in Git and must be obtained separately.

## Explicit Statement

Phase 3 remains pending independent review. This fix does not mark Phase 3 as accepted.

## Files Modified

1. `agent_solution/analysis/models.py` — Updated `SingleModelRuntimeConfig` dataclass
2. `agent_solution/model/config.py` — Updated configuration resolution
3. `agent_solution/model/runner.py` — Updated model runner for non-interactive completion
4. `agent_solution/model/README.md` — Updated configuration documentation
5. `.env.example` — Updated environment variable naming
6. `agent_solution/tests/test_local_model_runner.py` — Updated test fixtures
7. `agent_solution/tests/test_grounded_analysis.py` — Updated test fixtures

## Audit Link

[phase-03-FIX-01-non-interactive-local-completion-runtime.md](phase-03-FIX-01-non-interactive-local-completion-runtime.md)
