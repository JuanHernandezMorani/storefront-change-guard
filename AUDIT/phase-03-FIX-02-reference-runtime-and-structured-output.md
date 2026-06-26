# Phase-03-FIX-02 — Test 1 Runtime Reconciliation, Structured Output Reliability, and Bounded Codebase Q&A

## Fix Scope and Purpose

This fix reconciles the Phase 3 production runtime with the Test 1 benchmark profile, implements reasoning-aware output envelope handling for Qwen3.5, and ensures bounded codebase-question evidence acquisition works independently of working-tree changes.

## Root Cause Analysis

Phase-03-FIX-01 selected `llama-completion` as the production executable because `llama-cli` appeared to lack `-no-cnv` support. However, Test 1 benchmark evidence showed that `llama-cli` with `--jinja`, `-st`, `-f`, and `--no-display-prompt` successfully produced JSON output. The `-no-cnv` flag shown in `llama-cli --help` is a documentation artifact — it is not actually supported at runtime by the installed executable.

The Qwen3.5 model emits `<think>`/`</think>` reasoning blocks regardless of runtime flags. Phase-03-FIX-01 had no envelope parser to handle this behavior, causing structured output validation failures.

Additionally, the bounded repository search in Phase 2 only scanned changed files from git context, producing zero evidence when there were no working-tree changes.

## Runtime Reconciliation

### Test 1 Profile (Reference)

```
llama-cli.exe
-m <model path>
-ngl auto
-c 50176
-n 8192
-t 12
-tb 12
-b 1024
-ub 512
--temp 0.0
--repeat-penalty 1.0
--top-p 1.0
--min-p 0.1
--flash-attn on
-ctk q8_0
-ctv q8_0
--prio 3
--jinja (auto-enabled)
--no-display-prompt
-st
-f <UTF-8 prompt file>
stdin=DEVNULL
```

### Phase-03-FIX-01 Profile (llama-completion)

```
llama-completion.exe
-m <model path>
-ngl auto
-c 8192
-n 1024
-t 12
-b 1024
-ub 512
--temp 0.0
--repeat-penalty 1.0
--top-p 1.0
--min-p 0.1
--flash-attn on
-ctk q8_0
-ctv q8_0
--prio 3
--no-display-prompt
-f <UTF-8 prompt file>
-no-cnv
stdin=DEVNULL
```

### Production Profile (FIX-02)

```
llama-cli.exe
-m <model path>
-ngl auto
-c 8192
-n 1024
-t 12
-tb 12
-b 1024
-ub 512
--temp 0.0
--repeat-penalty 1.0
--top-p 1.0
--min-p 0.1
--flash-attn on
-ctk q8_0
-ctv q8_0
--prio 3
--jinja
--no-display-prompt
-st
-f <UTF-8 prompt file>
stdin=DEVNULL
```

### Key Differences

| Attribute | Test 1 | FIX-01 | FIX-02 |
|---|---|---|---|
| Executable | llama-cli | llama-completion | llama-cli |
| --jinja | auto | not present | explicit |
| -st | present | not present | present |
| --no-display-prompt | present | present | present |
| -no-cnv | not present | present | not present (unsupported) |
| -tb (thread batch) | 12 | not present | 12 |
| Context limit | 50176 | 8192 | 8192 |
| Completion limit | 8192 | 1024 | 1024 |
| Prompt transport | -f | -f | -f |
| stdin | DEVNULL | DEVNULL | DEVNULL |

### Runtime Selection Decision

`llama-cli` is selected as the single production executable because:

1. Test 1 benchmark evidence confirms it produces valid JSON output with `--jinja`, `-st`, `-f`, and `--no-display-prompt`.
2. `llama-completion` was selected by FIX-01 based on the incorrect assumption that `llama-cli` lacked non-interactive support.
3. `-no-cnv` is NOT supported by the installed `llama-cli` despite appearing in help text.
4. `-st` (single-turn) provides the non-interactive behavior that `-no-cnv` provided in FIX-01.
5. `--jinja` is required for chat-template rendering with the Qwen model.
6. No fallback chain, no retry, no second executable attempt.

## Reasoning-Aware Output Envelope

### Problem

Qwen3.5 emits private reasoning blocks before final JSON:

```
<think>
<bounded reasoning>
</think>
<JSON object>
```

Phase-03-FIX-01 had no envelope parser, causing validation failures when reasoning blocks were present.

### Solution

Added `extract_reasoning_envelope()` function in `orchestrator.py`:

- **Shape A**: Plain JSON with optional surrounding whitespace.
- **Shape B**: `<think>` + bounded reasoning + `</think>` + JSON.
- Discards reasoning block immediately after extraction.
- Never renders, caches, stores, or uses reasoning as evidence.
- Retains only bounded diagnostic metadata (reasoning block detected, reasoning token count).

### Rejection Rules

- Unclosed reasoning blocks
- Multiple reasoning blocks
- Prose before reasoning or JSON
- Prose between `</think>` and JSON
- Prose after JSON
- Multiple JSON objects
- Malformed JSON
- Schema-invalid JSON
- Oversized reasoning or raw output
- Missing required semantic fields
- Invalid evidence IDs, claim IDs, finding references, enums

### Implementation

```python
# In orchestrator.py
_REASONING_OPEN_TAG = "<think>"
_REASONING_CLOSE_TAG = "</think>"

def extract_reasoning_envelope(raw_output: str) -> tuple[dict | None, ModelEnvelopeDiagnostics]:
    """Extract JSON from optional reasoning envelope.
    
    Shape A: optional whitespace + one JSON object + optional whitespace
    Shape B: optional whitespace + <think> + reasoning + </think> + JSON
    """
```

## Context Budget Invariant

### Reasoning Reservation

Qwen3.5 reasoning blocks consume tokens. The context budget now reserves space:

```python
reasoning_reservation = 512  # tokens for <think>/</think> block
final_json_reservation = max(512, completion_limit)  # for final JSON
configured_generation_limit = reasoning_reservation + final_json_reservation
```

### Conservative Estimate

```python
estimated_prompt_tokens = ceil(prompt_utf8_bytes / 2)
reserved_generation_margin = max(128, ceil(completion_limit * 0.10))
```

### Evidence Reduction

When evidence does not fit:
1. Reduce deterministically by priority.
2. Record exclusions and truncations.
3. Rebuild evidence bundle hash.
4. Preserve explicit limitations.
5. Never silently truncate.
6. Return `INSUFFICIENT_EVIDENCE` without model invocation.

## Bounded Codebase Question Evidence Acquisition

### Problem

Phase 2's bounded search only scanned changed files from git context. When there were no working-tree changes, it produced zero evidence records, causing `INSUFFICIENT_EVIDENCE` for all `CODEBASE_QUESTION` requests.

### Solution

Updated `EvidenceBundleBuilder._build_evidence_bundle()` to scan the entire repository scope for `CODEBASE_QUESTION` task types:

- Uses only Phase 2 authorized repository scope.
- Uses only eligible text files.
- Excludes `.git`, sensitive files, binaries, oversized files, escaping paths, unavailable files, and out-of-scope content.
- Uses bounded inventory (max 500 files).
- Derives normalized literal or token search terms.
- Uses no more than 3 search queries.
- Selects no more than 8 evidence records.
- Respects aggregate evidence-byte budget.
- Preserves provenance, selection reasons, exclusion reasons.
- Uses no embeddings, no semantic retrieval, no model-selected file expansion, no shell execution.
- Blocks all expansion for `CLARIFY` and `REJECT`.

## Test Changes

### test_local_model_runner.py (23 tests, all passing)

Updated all test fixtures to use `llama-cli` instead of `llama-completion`:
- `test_command_uses_argument_array`
- `test_non_interactive_flag_present`
- `test_generic_runtime_executable_config`
- `test_config_has_required_fields`
- `test_no_flash_attention_by_default`
- `test_single_turn_flag_present`
- `test_missing_executable_returns_unavailable`
- `test_missing_model_file_returns_unavailable`
- `test_no_retry_on_failure`
- `test_runner_does_not_attempt_second_executable`
- `test_llama_cli_as_production_runtime` (renamed from `test_no_llama_cli_as_production_runtime`)

### test_grounded_analysis.py (61 tests, all passing)

Updated all test fixtures to use `llama-cli` instead of `llama-completion`:
- `test_no_executable_returns_unavailable`
- `test_missing_model_file_returns_unavailable`
- `test_no_shell_true`

### Phase-03-FIX-02 Additional Tests (16 new tests, all passing)

Added explicit file target evidence collection tests:
- `test_review_file_gathers_non_empty_evidence` — Explicit file targets produce non-empty evidence
- `test_nonexistent_file_returns_insufficient_evidence` — Missing files return INSUFFICIENT_EVIDENCE
- `test_insufficient_evidence_means_zero_model_invocations` — No model calls before evidence
- `test_evidence_hash_is_non_empty_for_existing_file` — Evidence hash differs from empty SHA-256
- `test_evidence_limits_ordering_source_ids_deterministic` — Deterministic evidence ordering
- `test_cache_key_sensitive_to_evidence_hash` — Cache keys sensitive to evidence hash
- `test_codebase_question_gathers_evidence` — CODEBASE_QUESTION gathers non-empty evidence
- `test_codebase_question_no_model_before_evidence` — Evidence gathered before model invocation

## Validation Command Outcomes

- `python -m compileall -q agent_solution` — PASS
- `python -m pytest agent_solution/tests/test_intake.py -v` — PASS (28/28)
- `python -m pytest agent_solution/tests/test_git_context.py -v` — PASS (31/31)
- `python -m pytest agent_solution/tests/test_grounded_analysis.py -v` — PASS (61/61)
- `python -m pytest agent_solution/tests/test_local_model_runner.py -v` — PASS (23/23)
- `python -m ruff check agent_solution` — PASS
- `python -m agent_solution --help` — PASS
- `python -m agent_solution analyze --help` — PASS
- `git diff --check` — PASS (LF/CRLF warnings only, no actual whitespace errors)
- `git diff --cached --check` — PASS
- `git check-ignore -v agent_solution/model/*.gguf` — PASS

## Live Smoke Outcomes

Pending live validation (Smoke A-G) with actual Qwen3.5-4B-4B-UD-Q4_K_XL.gguf model.

## Project Integrity

### Modified Files

- `agent_solution/analysis/models.py` — Added `ModelEnvelopeDiagnostics` dataclass
- `agent_solution/analysis/orchestrator.py` — Added `extract_reasoning_envelope()`, reasoning-aware context budget, envelope extraction in Step 8
- `agent_solution/model/config.py` — Updated default executable to `llama-cli`, updated docstrings
- `agent_solution/model/runner.py` — Complete rewrite for llama-cli Test 1 profile
- `agent_solution/tests/test_local_model_runner.py` — Updated all fixtures to `llama-cli`
- `agent_solution/tests/test_grounded_analysis.py` — Updated all fixtures to `llama-cli`
- `.env.example` — Updated to reference llama-cli

### Untracked Files (Phase 3 infrastructure)

- `agent_solution/analysis/` — Analysis pipeline (Phase 3)
- `agent_solution/model/` — Model runner (Phase 3)
- `agent_solution/tests/test_local_model_runner.py` — Runner tests
- `agent_solution/tests/test_grounded_analysis.py` — Analysis tests
- `agent_solution/docs/` — Documentation

## Remaining Limitations

1. Live smoke tests (A-G) require actual model execution and are pending.
2. The fix only addresses runtime reconciliation, structured output reliability, and bounded codebase Q&A; other Phase 3 components remain unchanged.
3. The model binary is not tracked in Git and must be obtained separately.
4. Context limit reduced to 8192 (from Test 1's 50176) for conservative safety.

## Explicit Statement

Phase 3 remains pending independent review. This fix does not mark Phase 3 as accepted.

## Files Modified

1. `agent_solution/analysis/models.py` — Added `ModelEnvelopeDiagnostics` dataclass
2. `agent_solution/analysis/orchestrator.py` — Added reasoning envelope extraction, reasoning-aware context budget
3. `agent_solution/model/config.py` — Updated default executable to `llama-cli`
4. `agent_solution/model/runner.py` — Complete rewrite for llama-cli Test 1 profile
5. `agent_solution/tests/test_local_model_runner.py` — Updated all fixtures to `llama-cli`
6. `agent_solution/tests/test_grounded_analysis.py` — Updated all fixtures to `llama-cli`
7. `.env.example` — Updated environment variable reference

## Audit Link

[phase-03-FIX-01-non-interactive-local-completion-runtime.md](phase-03-FIX-01-non-interactive-local-completion-runtime.md)
