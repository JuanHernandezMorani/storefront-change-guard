# Prompt Record — Phase 03 Grounded Analysis

## Metadata

| Field | Value |
|---|---|
| Prompt ID | prompt-008-phase-03-grounded-analysis-single-local-model |
| Phase | Phase 03 |
| Date | 2026-06-24 |
| Model Used | mimo-v2.5-free (opencode/mimo-v2.5-free) |

---

## Task Description

Implement Phase 03 of the storefront-change-guard project: Evidence-Grounded Semantic Analysis with One Local Model.

### Requirements

1. Implement a local, evidence-grounded semantic analysis layer
2. Use exactly one local model runtime (Qwen3.5-4B-UD-Q4_K_XL.gguf)
3. Produce actionable code-review analysis
4. Answer codebase questions from bounded repository evidence
5. Explain when evidence is insufficient
6. Produce evidence summaries without making final readiness decisions
7. Preserve citations, limitations, and claim status in structured output
8. Cache valid analysis results using SQLite
9. Persist compact session state without raw transcripts
10. Fail explicitly when model is unavailable, times out, or produces invalid output

---

## Implementation Approach

### Architecture

1. **Analysis Models** (`analysis/models.py`) - All typed data contracts
2. **Model Config** (`model/config.py`) - SingleModelRuntimeConfig
3. **Model Runner** (`model/runner.py`) - LocalModelRunner using subprocess
4. **Evidence Builder** (`analysis/evidence.py`) - EvidenceBundleBuilder
5. **Output Validator** (`analysis/validator.py`) - OutputValidator
6. **Result Renderer** (`analysis/renderer.py`) - ResultRenderer
7. **Analysis Cache** (`analysis/cache.py`) - SQLite-backed cache
8. **Session Store** (`analysis/session.py`) - SQLite-backed session state
9. **Orchestrator** (`analysis/orchestrator.py`) - AnalysisOrchestrator
10. **CLI** (`cli.py`) - Added analyze subcommand

### Key Design Decisions

1. **Single model** - No fallbacks, no routing, no cloud APIs
2. **Deterministic pipeline** - Intake → Evidence → Model (1 invocation) → Validate → Render
3. **SQLite cache** - Deterministic keys with fingerprint-based invalidation
4. **Claim policy** - VERIFIED, INFERRED, UNKNOWN, OUT_OF_SCOPE statuses
5. **Anti-loop** - max_model_invocations_per_request = 1

---

## Files Created/Modified

### New Files (16)

1. `agent_solution/analysis/__init__.py`
2. `agent_solution/analysis/models.py`
3. `agent_solution/analysis/evidence.py`
4. `agent_solution/analysis/validator.py`
5. `agent_solution/analysis/renderer.py`
6. `agent_solution/analysis/cache.py`
7. `agent_solution/analysis/session.py`
8. `agent_solution/analysis/orchestrator.py`
9. `agent_solution/model/__init__.py`
10. `agent_solution/model/config.py`
11. `agent_solution/model/runner.py`
12. `agent_solution/model/README.md`
13. `agent_solution/model/model-manifest.example.json`
14. `agent_solution/model/.gitignore`
15. `agent_solution/tests/test_grounded_analysis.py`
16. `agent_solution/tests/test_local_model_runner.py`

### Modified Files (4)

1. `agent_solution/cli.py` - Added analyze subcommand
2. `pyproject.toml` - Added analysis and model packages
3. `.env.example` - Added Phase 3 environment variables
4. `.gitignore` - Updated model file patterns

---

## Validation Results

| Command | Result |
|---|---|
| `python -m compileall -q agent_solution` | PASS |
| `python -m pytest agent_solution/tests/test_intake.py -v` | PASS (28/28) |
| `python -m pytest agent_solution/tests/test_git_context.py -v` | PASS (31/31) |
| `python -m pytest agent_solution/tests/test_grounded_analysis.py -v` | PASS (47/47) |
| `python -m pytest agent_solution/tests/test_local_model_runner.py -v` | PASS (13/13) |
| `python -m ruff check agent_solution` | PASS |
| `python -m agent_solution --help` | PASS |
| `python -m agent_solution analyze --help` | PASS |
| `git diff --check` | PASS |
| `git diff --cached --check` | PASS |
| `git check-ignore -v agent_solution/model/Qwen3.5-4B-UD-Q4_K_XL.gguf` | PASS |

---

## Status

Implementation complete — pending independent review.
