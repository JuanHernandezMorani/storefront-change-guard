# Changelog

All notable changes to this project are documented here.

## [0.5.0] — 2026-06-26

### Added

- Tracked delivery runners under `scripts/` for Phase 04 live patch validation
  and Phase 05 live readiness evaluation.
- Phase 06 delivery-readiness audit, challenge coverage matrix, delivery
  manifest, and final execution summaries.
- Successful Phase 04 and Phase 05 machine-readable artifacts to the delivery
  bundle.

### Changed

- Selected `Qwen3.5-9B-UD-IQ3_XXS.gguf` as the one active Phase 03 product
  runtime after controlled structured-output evidence.
- Phase 03 live gate runner now uses portable repository-relative defaults and
  persists future artifacts under `artifacts/phase03-live/`.
- Updated documentation to reflect completed Phase 03 gates, Phase 04
  validation, and Phase 05 `READY` decision.

### Fixed

- Derived analysis runtime identity from the active GGUF filename rather than a
  hardcoded 4B label.
- Prioritized explicit requested file scope over unrelated working-tree diffs
  for evidence collection and cache eligibility.
- Accepted safe ASCII Spanish file-scoped Q&A in the live runner without
  relying on PowerShell Unicode source decoding.
- Canonicalized Phase 05 JSON inputs to UTF-8 without a BOM before Python
  artifact loading.

## [0.4.0] — 2026-06-26

### Added

- Phase 04 deterministic isolated patch validation with static unified-diff
  safety checks, detached Git worktrees, fixed validation profiles, and
  machine-readable artifacts.
- Phase 05 deterministic readiness policy consuming Phase 03/04 JSON artifacts.
- Phase-scoped deterministic test runner and PowerShell wrapper.

### Fixed

- Strict runtime-boundary handling for observed `llama-cli` wrappers and one
  complete leading thinking envelope. Raw model reasoning is not retained.

## [0.3.0] — 2026-06-24

### Added

- Phase 03 evidence-grounded semantic analysis with one local model,
  deterministic evidence validation, structured result rendering, cache, and
  session state.

## [0.2.1] — 2026-06-24

### Added

- Phase 02B Git context collection, repository fingerprinting, bounded changed
  file discovery, and safe excerpt collection.

## [0.2.0] — 2026-06-24

### Fixed

- Phase 02 intake decision contract and deterministic mixed-goals detection.

## [0.1.0] — 2026-06-23

### Added

- Project bootstrap, controlled storefront preparation, and initial intake gate.
