# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.3.0] — 2026-06-24

### Added

- **Phase 03:** Evidence-Grounded Semantic Analysis with One Local Model.
  - Created 18 typed data contracts (frozen dataclasses) for analysis models.
  - Implemented LocalModelRunner using llama.cpp CLI with subprocess (shell=False).
  - Implemented EvidenceBundleBuilder consuming Phase 2 intake and Git context.
  - Implemented deterministic evidence-expansion pass within Phase 2 scope.
  - Implemented OutputValidator for model JSON output with claim policy enforcement.
  - Implemented ResultRenderer for structured output with language support.
  - Implemented SQLite-backed AnalysisCache with deterministic keys.
  - Implemented SQLite-backed SessionStateStore with compact structured state.
  - Implemented AnalysisOrchestrator coordinating full pipeline.
  - Added analyze subcommand to CLI with --request, --repository, --language, --format, --state-dir, --no-cache, --session-id options.
  - Created 47 test cases for grounded analysis (all passing).
  - Created 13 test cases for local model runner (all passing).
  - Single-model configuration only - no fallback, no routing, no cloud APIs.
  - Anti-loop limits enforced (max_model_invocations_per_request = 1).
  - Prompt-injection resistance for repository evidence.
  - English and Spanish language support.
  - Model GGUF file properly ignored by Git.

### Fixed

- **Phase-03-FIX-01:** Non-Interactive Local Completion Runtime.
  - Replaced `llama-cli` with `llama-completion` as the configured single-turn local completion executable.
  - Added `-no-cnv` flag for non-interactive completion mode.
  - Implemented safe prompt transport using temporary files (`-f` flag) instead of `-p` argument.
  - Migrated configuration from `STORE_FRONT_GUARD_LLAMA_CLI` to `STORE_FRONT_GUARD_LLAMA_EXECUTABLE`.
  - Removed hardcoded path auto-discovery; user must provide explicit executable path.
  - Updated `SingleModelRuntimeConfig` dataclass with generic executable fields.
  - Improved timeout and process-cleanup behavior for Windows.
  - Updated 19 test cases in `test_local_model_runner.py` for new configuration.
  - Updated 4 test cases in `test_grounded_analysis.py` for new configuration.
  - All validation commands pass (compileall, tests, ruff, CLI help, git checks).

- **Phase-03-FIX-02:** Test 1 Runtime Reconciliation, Structured Output Reliability, Bounded Codebase Q&A.
  - Reconciled production runtime with Test 1 benchmark profile: `llama-cli` with `--jinja`, `-st`, `-f`, `--no-display-prompt`, stdin=DEVNULL.
  - Replaced `llama-completion` (FIX-01) with `llama-cli` as the single production executable based on Test 1 evidence.
  - Added reasoning-aware output envelope parser (`extract_reasoning_envelope`) supporting Shape A (plain JSON) and Shape B (`<think>`/`</think>` envelope).
  - Reasoning blocks discarded immediately after extraction; never cached, stored, rendered, or used as evidence.
  - Added reasoning reservation (512 tokens) and final JSON reservation (max(512, completion_limit)) to context budget.
  - Updated bounded repository search to scan entire repository for `CODEBASE_QUESTION` (not just changed files).
  - Added `explicit_file_targets` to `ResolvedScope` and `extract_file_targets` to classifier for explicit file target evidence collection.
  - Updated `EvidenceBundleBuilder` to include explicit file target evidence for `CODE_REVIEW` and `BUG_DIAGNOSIS` task types.
  - Updated orchestrator to check for empty evidence records and enforce context budget invariant.
  - Strengthened system prompt to require JSON after optional `<think>` block.
  - Updated all test fixtures in `test_local_model_runner.py` (23 tests) and `test_grounded_analysis.py` (61 tests) for `llama-cli`.
  - All 182 deterministic tests pass (intake: 28, git_context: 31, grounded_analysis: 61, local_model_runner: 23, unit: 1, explicit_file_target: 6, codebase_question: 2).
  - Live smoke tests (A-G) pending actual model execution.

---

## [0.2.0] — 2026-06-24

### Fixed

- **Phase-02-FIX-01:** Intake decision contract and mixed-goals detection.
  - Added validation-command and expected-behavior patterns to PATCH_PROPOSAL classifier, enabling HIGH-confidence classification for explicit patch requests.
  - Replaced keyword-count mixed-goals heuristic with deterministic task-signal overlap detection.
  - Mixed-goal requests now always return CLARIFY with explicit decomposition clarification explaining different execution contracts per task type.
  - Patch proposals can no longer receive ACCEPT_WITH_SAFE_DEFAULTS; they require REFINE_FOR_EXECUTION with explicit worktree-only constraints or CLARIFY.
  - Added bilingual (EN/ES) decomposition questions for mixed-goal requests.
  - Fixed all 17 Ruff warnings in scoped intake files.
  - Added 7 new test classes (28 total tests, all passing).
  - Updated documentation with patch proposal decision contract, mixed-goals detection mechanism, and worktree-only invariant.

## [0.2.1] — 2026-06-24

### Added

- **Phase 02B:** Git Context Collection, Deterministic Evidence Snapshot, Repository Fingerprinting, Bounded Changed-File Discovery, Safe Excerpt Collection.
  - Created 12 typed data contracts (frozen dataclasses) for Git context evidence.
  - Implemented deterministic repository fingerprinting with SHA-256 hashing for cache invalidation.
  - Implemented bounded changed-file discovery with 4 scope modes (working_tree_diff, explicit_paths, bounded_repository_search, no_actionable_scope).
  - Implemented safe file excerpt collection with sensitive/binary/oversized handling.
  - Implemented read-only Git command execution with argument arrays, timeouts, and provenance tracking.
  - Implemented intake integration respecting Phase 2A decisions.
  - Created 31 test cases using temporary Git repositories (all passing).
  - Created technical documentation and validation reports.

## [0.1.0] — 2026-06-23

### Added

- Phase 0: Project bootstrap, CLI entry point, repository structure.
- Phase 1: Demo storefront preparation with checkout rules and monetary invariant.
- Phase-01-FIX-01: Context provider boundary remediation.
- Phase-01-FIX-02: Monetary integer-cent validation and review-governance normalization.
- Phase 2A: Request Intake and Prompt Quality Gate foundation (classification, validation, safe defaults, clarification, model-profile placeholders).

- **Phase-02-FIX-02:** Natural Single-Purpose English and Spanish Intake.
  - Added defect-discovery patterns (find/identify defect, encontrar/encontrar defecto) to BUG_DIAGNOSIS classifier.
  - Added codebase-question patterns (what does...do, que hace...hace) to CODEBASE_QUESTION classifier.
  - Added Spanish review pattern (hace una revision) to CODE_REVIEW classifier.
  - Added plural bug pattern (bugs) and edit-code pattern to PATCH_PROPOSAL classifier.
  - Added constraint-phrase stripping (do not modify, no modifiques, only, return the answer in Spanish, etc.) before classification and mixed-goals detection.
  - Updated _determine_decision to accept bounded file review (CODE_REVIEW with has_paths) and bounded defect discovery (BUG_DIAGNOSIS with has_paths) as ACCEPT_WITH_SAFE_DEFAULTS.
  - Updated _assess_risk to treat bounded defect discovery as LOW risk.
  - Updated _resolve_scope to describe bounded file review and bounded defect discovery scopes.
  - Updated resolve_safe_defaults to apply safe defaults for bounded file review and bounded defect discovery.
  - Added 26 regression tests covering English acceptance, Spanish acceptance, constraint handling, retained rejections, and Fix-the-bug CLARIFY preservation.
  - All 54 intake tests pass; ruff clean; git diff --check clean.

- **Phase-02-FIX-02 (post-review):** Narrow Spanish review pattern and negative patch constraint.
  - Replaced broad Spanish review regex (hac[ée] (una|uma) revis[io]?[áaóõã]?n?) with narrow Spanish-only pattern (hac[ée] una revis[io]?[áaó]?n?) that accepts "Hacé una revisión de código de shipping.py." and rejects Portuguese-only phrasing such as "Faça uma revisão de shipping.py.".
  - Added "do not apply" and "don't apply" constraint patterns to policy.py so that "Do not apply a patch." and "Review shipping.py. Do not apply a patch." remain bounded reviews (CODE_REVIEW + ACCEPT_WITH_SAFE_DEFAULTS), not PATCH_PROPOSAL.
  - Retained affirmative patch behavior: "Apply the patch to shipping.py." continues to classify as PATCH_PROPOSAL.
  - Added 4 regression tests covering negative patch constraint, affirmative patch retention, and Portuguese rejection.
  - All intake tests pass; ruff clean; git diff --check clean.
