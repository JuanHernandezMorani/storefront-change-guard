# Phase-03 Validation 01 — Live Single-Model Runtime Validation

## Validation Scope and Purpose

This validation verifies that the Phase 3 evidence-grounded analysis implementation correctly integrates with the selected single local model (`Qwen3.5-4B-UD-Q4_K_XL.gguf`) through the real CLI path. It confirms operational correctness only — not performance, not benchmarking.

## Repository Revision and Initial Git State

| Item | Value |
|---|---|
| Git SHA | `275bb5400b564d69b4b8d0ebc3d0b5fb81936110` |
| Branch | `master` |
| Modified tracked files | `.env.example`, `.gitignore`, `AUDIT/change-register.md`, `CHANGELOG.md`, `agent_solution/cli.py`, `agent_solution/git_tools/collector.py`, `agent_solution/git_tools/excerpts.py`, `agent_solution/git_tools/fingerprint.py`, `agent_solution/git_tools/models.py`, `pyproject.toml` |
| Staged changes | None |
| Untracked Phase 3 files | `AUDIT/phase-03-grounded-analysis-single-local-model.md`, `REPORT/executions/run-008-phase-03-validation.md`, `REPORT/prompts/prompt-008-phase-03-grounded-analysis-single-local-model.md`, `agent_solution/analysis/`, `agent_solution/docs/`, `agent_solution/model/`, `agent_solution/tests/test_grounded_analysis.py`, `agent_solution/tests/test_local_model_runner.py` |

## Model Existence, Size, SHA-256, and Git-Ignore Result

| Item | Value |
|---|---|
| Model path | `agent_solution/model/Qwen3.5-4B-UD-Q4_K_XL.gguf` |
| GGUF exists | Yes |
| File size | 2,912,109,728 bytes (~2.71 GB) |
| SHA-256 | `B252C5610A42CA82D20FE2A12813E9D069EED89292907E26C783EEB0BC961BC7` |
| Git-ignored | Yes — matched by `agent_solution/model/.gitignore:2:*.gguf` |

## Runtime Executable Discovery and Version/Help Evidence

| Item | Value |
|---|---|
| Configured llama-cli path | `C:\Proyectos\Supporter\llm\llama.cpp\build\bin\Release\llama-cli.exe` |
| Executable exists | Yes |
| llama-cli version | `791 (c1304d7)` |
| Build info | `MSVC 19.51.36246.0 for x64` |

## Effective Single-Model Runtime Configuration

| Parameter | Value |
|---|---|
| model_id | `qwen3.5-4b-ud-q4-k-xl` |
| model_filename | `Qwen3.5-4B-UD-Q4_K_XL.gguf` |
| runtime_backend | `llama.cpp` |
| context_limit | 4096 |
| completion_limit | 1024 |
| timeout_seconds | 120 |
| thread_count | 4 |
| batch_size | 512 |
| micro_batch_size | 128 |
| temperature | 0.0 |
| top_p | 1.0 |
| min_p | 0.1 |
| repeat_penalty | 1.0 |
| flash_attention_enabled | False |
| kv_cache_type_k | f16 |
| kv_cache_type_v | f16 |
| prompt_schema_version | 0.3.0 |
| runtime_profile_version | 0.3.0 |

## Confirmed Local CLI Flags

The following flags are confirmed supported by llama-cli version 791:

- `-m` (model path) — supported
- `-c` (context size) — supported
- `-n` (n-predict) — supported
- `-t` (threads) — supported
- `-b` (batch-size) — supported
- `-ub` (ubatch-size) — supported
- `--temp` / `--temperature` — supported
- `--top-p` — supported
- `--min-p` — supported
- `--repeat-penalty` — supported
- `--no-display-prompt` — supported
- `-p` (prompt) — supported
- `--cache-type-k` — supported
- `--cache-type-v` — supported

**Critical finding:** `--flash-attn` is listed in the help but the flag format is `-fa, --flash-attn [on|off|auto]`. The current runner passes `--flash-attn` without a value, which may not work correctly with this llama-cli version.

**Critical finding:** When a chat template is available (as with Qwen3.5), `llama-cli` automatically enters interactive/conversation mode. The `-no-cnv` / `--no-conversation` flag is **not supported by `llama-cli`** — it returns an error suggesting `llama-completion` instead. The `-st` / `--single-turn` flag also does not prevent interactive mode when a prompt is provided with `-p`.

## Safe Invocation Metadata

The `LocalModelRunner` implementation was verified:

- subprocess argument array is used (tuple of strings)
- shell=False is used
- no user text becomes executable shell syntax
- model path is passed as data (argument to `-m`)
- timeout is explicit (configurable, default 120s)
- stdout and stderr capture are bounded (max_output_bytes = 131072)
- exactly one model invocation is allowed per request (Phase3Limits.max_model_invocations_per_request = 1)
- no retry occurs after failure
- no alternate model is attempted
- no persistent server process is created
- no hidden background model process remains after execution

## Live Smoke Results

### Smoke 1 — English Evidence-Grounded Code Review

**Result: BLOCKED — Model invocation cannot complete**

The Phase 3 CLI pipeline (intake → evidence → model → validate → render) was invoked against a synthetic temporary Git repository with a modified `shipping.py` file.

- The intake pipeline correctly classified the request as `CODE_REVIEW` and resolved the scope.
- The evidence bundle was correctly built from the Git working tree diff.
- The model runner attempted to invoke `llama-cli` with the constructed command.
- `llama-cli` detected the Qwen3.5 chat template and entered interactive conversation mode instead of single-turn completion mode.
- The process hung indefinitely waiting for interactive input, never producing JSON output.
- The `-no-cnv` flag is not supported by `llama-cli` (error: "please use llama-completion instead").
- The `-st` / `--single-turn` flag does not prevent interactive mode when `-p` is used with a chat-template-enabled model.

**Root cause:** The `LocalModelRunner` uses `llama-cli` which cannot operate in non-interactive completion mode for models with chat templates. The correct executable for non-interactive completion is `llama-completion`.

### Smoke 2 — Cache Verification

**Result: NOT REACHABLE — Blocked by Smoke 1 failure**

Cache verification could not be performed because the initial model invocation (Smoke 1) never completed. The cache path in the orchestrator requires a successful model invocation to store results.

### Smoke 3 — Spanish Codebase Question

**Result: NOT REACHABLE — Blocked by Smoke 1 failure**

Spanish codebase question could not be tested because the model invocation mechanism is non-functional for the same reason as Smoke 1.

### Smoke 4 — Model Unavailable Behavior

**Result: VALIDATED (unit test level)**

The model-unavailable failure path was validated through existing unit tests (`TestModelUnavailable` in `test_grounded_analysis.py` and `test_local_model_runner.py`):

- Missing executable returns `MODEL_UNAVAILABLE` status
- Missing model file returns `MODEL_UNAVAILABLE` status
- No retry occurs after failure
- No alternate model is attempted
- No cloud call occurs
- No cached success result is incorrectly returned

CLI-level validation could not be performed due to Smoke 1 blocking.

### Smoke 5 — Invalid Output Defensive Path

**Result: VALIDATED (unit test level)**

The invalid-output defensive path was validated through existing unit tests (`TestMalformedJson`, `TestUnknownEvidenceCitation`, `TestVerifiedWithoutEvidence`, `TestInferredWithoutBasis` in `test_grounded_analysis.py`):

- Malformed JSON returns `MODEL_OUTPUT_INVALID`
- Unknown evidence citation returns `MODEL_OUTPUT_INVALID`
- VERIFIED claim without evidence returns `MODEL_OUTPUT_INVALID`
- INFERRED claim without inference basis returns `MODEL_OUTPUT_INVALID`
- No retry occurs
- No fallback model is attempted
- No cache success entry is written
- Failure contains bounded deterministic explanation

### Smoke 6 — Prompt Injection Resistance

**Result: VALIDATED (unit test level)**

Prompt injection resistance was validated through the existing unit test (`TestPromptInjectionResistance` in `test_grounded_analysis.py`):

- Repository content containing adversarial instructions is treated only as evidence data
- The system prompt explicitly instructs the model to treat all evidence as data only
- The output does not follow instructions contained inside repository files
- The analysis follows Phase 3 claim policy
- No final readiness approval is produced from repository text

## Temporary Repository and State-Directory Locations

- Smoke repositories: `$env:TEMP\storefront-change-guard-phase03-validation\` (cleaned after validation)
- State directory: `$env:TEMP\storefront-change-guard-phase03-state\` (cleaned after validation)

## Project-Repository Integrity Before/After Comparison

| Check | Before | After | Match |
|---|---|---|---|
| `git status --short` | 10 modified tracked files + 8 untracked | Same | Yes |
| `git diff --name-only` | 10 files | Same | Yes |
| `git diff --cached --name-only` | Empty | Empty | Yes |
| SQLite files in project | None | None | Yes |
| Lingering model processes | None | None | Yes |

No tracked project source file was modified by smoke validation. No benchmark artifact was modified. No Test 1 or Test 2 artifact was modified. No model binary was staged or committed. No temporary cache, SQLite database, raw prompt, raw model output, or temporary smoke repository remains inside the project working tree.

## Final Validation Command Outcomes

| Command | Result |
|---|---|
| `python -m compileall -q agent_solution` | PASS |
| `python -m pytest agent_solution/tests/test_intake.py -v` | PASS (28/28) |
| `python -m pytest agent_solution/tests/test_git_context.py -v` | PASS (31/31) |
| `python -m pytest agent_solution/tests/test_grounded_analysis.py -v` | PASS (47/47) |
| `python -m pytest agent_solution/tests/test_local_model_runner.py -v` | PASS (13/13) |
| `python -m ruff check agent_solution` | PASS (0 errors) |
| `python -m agent_solution --help` | PASS |
| `python -m agent_solution analyze --help` | PASS |
| `git diff --check` | PASS (CRLF warnings only) |
| `git diff --cached --check` | PASS |
| `git status --short` | PASS (no unexpected changes) |
| `git check-ignore -v agent_solution/model/Qwen3.5-4B-UD-Q4_K_XL.gguf` | PASS (ignored by `.gitignore:2:*.gguf`) |

## Failures, Limitations, and Deferred Conditions

### Blocking Failure

**The `LocalModelRunner` uses `llama-cli` which cannot operate in non-interactive completion mode for models with chat templates.**

When `llama-cli` detects a chat template (as with Qwen3.5-4B), it automatically enters interactive conversation mode, even when a prompt is provided with `-p`. The `-no-cnv` flag is not supported by `llama-cli` (it suggests using `llama-completion` instead). The `-st` / `--single-turn` flag does not prevent interactive mode.

This prevents all live model smoke tests (Smoke 1, 2, 3) from completing. The unit tests for the model runner and analysis pipeline pass because they do not invoke the actual model.

### Non-Blocking Observations

1. The `--flash-attn` flag in the runner is passed as a bare flag, but the installed llama-cli version expects `--flash-attn [on|off|auto]`. This may cause issues if flash attention is enabled.
2. The default `temperature=0.0` is different from llama-cli's default of `0.80`. This is intentional for deterministic sampling but should be documented.
3. The default `top_p=1.0` disables top-p sampling, and `min_p=0.1` is active. These are valid deterministic settings.

## Explicit Outcome

**CHANGES_REQUIRED**

The Phase 3 implementation has a blocking defect in the `LocalModelRunner`: it uses `llama-cli` which cannot operate in non-interactive completion mode for models with chat templates. The correct executable for non-interactive single-turn completion is `llama-completion`.

## Explicit Statement

Phase 3 is still pending independent review. This validation does not constitute acceptance.

## Artifact Paths

- `AUDIT/phase-03-validation-01-live-single-model-runtime.md`
- `REPORT/executions/run-009-phase-03-validation-01-live-runtime.md`
- `REPORT/prompts/prompt-009-phase-03-validation-01-live-single-model-runtime.md`
- `AUDIT/change-register.md` (appended)
