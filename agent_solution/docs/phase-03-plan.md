# Phase 03 Implementation Plan

## Summary

Implement a local, evidence-grounded semantic analysis layer using a single local Qwen3.5-9B-UD-IQ3_XXS model via llama.cpp CLI.

## New Files to Create

### 1. `agent_solution/analysis/__init__.py`
Module init for analysis package.

### 2. `agent_solution/analysis/models.py`
All typed data contracts:
- AnalysisStatus (enum): ANALYSIS_COMPLETED, ANALYSIS_CACHE_HIT, INTAKE_BLOCKED, INSUFFICIENT_EVIDENCE, MODEL_UNAVAILABLE, MODEL_TIMEOUT, MODEL_EXECUTION_FAILED, MODEL_OUTPUT_INVALID, EVIDENCE_VALIDATION_FAILED, PHASE_AUTHORITY_LIMIT
- ClaimStatus (enum): VERIFIED, INFERRED, UNKNOWN, OUT_OF_SCOPE
- Severity (enum): CRITICAL, HIGH, MEDIUM, LOW, INFO
- TaskType mapping to analysis modes
- EvidenceRecord (frozen dataclass)
- EvidenceBundle (frozen dataclass)
- Claim (frozen dataclass)
- AnalysisFinding (frozen dataclass)
- AnalysisRecommendation (frozen dataclass)
- GroundedAnalysisRequest (frozen dataclass)
- GroundedAnalysisResult (frozen dataclass)
- SingleModelRuntimeConfig (frozen dataclass)
- ModelExecutionResult (frozen dataclass)
- CollectionLimits for Phase 3

### 3. `agent_solution/analysis/evidence.py`
EvidenceBundleBuilder:
- Consumes Phase 2 IntakeContract and GitContextSnapshot
- Builds bounded evidence bundle
- Deterministic evidence expansion pass
- Search within Phase 2 scope
- Returns EvidenceBundle or INSUFFICIENT_EVIDENCE

### 4. `agent_solution/model/__init__.py`
Module init for model package.

### 5. `agent_solution/model/runner.py`
LocalModelRunner:
- Subprocess invocation of llama-cli
- shell=False, argument arrays
- Timeout handling
- Stdout/stderr bounded capture
- Returns ModelExecutionResult

### 6. `agent_solution/analysis/validator.py`
OutputValidator:
- Validates JSON structure
- Validates enums
- Validates evidence ID references
- Validates claim policy
- Validates finding-claim relationships
- Returns validated result or MODEL_OUTPUT_INVALID

### 7. `agent_solution/analysis/renderer.py`
ResultRenderer:
- Deterministic rendering from validated results
- Structured output with citations
- Language-aware rendering

### 8. `agent_solution/analysis/cache.py`
AnalysisCache:
- SQLite-backed cache
- Deterministic cache key computation
- Cache invalidation on fingerprint change
- Compact storage

### 9. `agent_solution/analysis/session.py`
SessionStateStore:
- SQLite-backed session state
- Compact structured state only
- No raw transcripts
- Fingerprint-aware invalidation

### 10. `agent_solution/analysis/orchestrator.py`
AnalysisOrchestrator:
- Coordinates full pipeline
- Intake -> Evidence -> Model -> Validate -> Render
- Anti-loop limits
- Single model invocation

### 11. `agent_solution/model/config.py`
Runtime configuration for the single model.

### 12. `agent_solution/tests/test_grounded_analysis.py`
30 test cases covering all required scenarios.

### 13. `agent_solution/tests/test_local_model_runner.py`
Tests for model runner and runtime configuration.

### 14. `agent_solution/model/README.md`
Model documentation.

### 15. `agent_solution/model/model-manifest.example.json`
Example manifest.

### 16. `agent_solution/model/.gitignore`
Ignore model binaries.

## Files to Modify

### 1. `agent_solution/cli.py`
Add `analyze` subcommand with:
- --request
- --repository
- --language auto|en|es
- --format json|text
- --state-dir
- --no-cache
- --session-id

### 2. `pyproject.toml`
Add `agent_solution.analysis` and `agent_solution.model` to packages.

### 3. `.gitignore`
Ensure model files are ignored (already partially done).

### 4. `.env.example`
Update with Phase 3 environment variables.

### 5. `AUDIT/change-register.md`
Append Phase 03 record.

### 6. `CHANGELOG.md`
Append Phase 03 entry.

## Implementation Order

1. Models (analysis/models.py)
2. Runtime config (model/config.py)
3. Model runner (model/runner.py)
4. Evidence bundle builder (analysis/evidence.py)
5. Output validator (analysis/validator.py)
6. Result renderer (analysis/renderer.py)
7. Analysis cache (analysis/cache.py)
8. Session state store (analysis/session.py)
9. Analysis orchestrator (analysis/orchestrator.py)
10. CLI integration (cli.py)
11. Tests
12. Documentation
13. Audit records
14. Validation


## Historical plan note

This file records the implementation plan. The completed Phase 03 runtime and final model decision are documented in `../../docs/model-selection.md` and `../../REPORT/executions/run-015-phase-03-live-gates.md`.
