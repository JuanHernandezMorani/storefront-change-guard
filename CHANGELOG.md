# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

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
