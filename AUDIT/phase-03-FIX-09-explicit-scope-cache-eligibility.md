# Phase-03-FIX-09 — Explicit-Scope Cache Eligibility

## Live-gate finding

Gate A completed successfully for `Review shipping.py.` using the selected 9B local model. Gate B repeated the same request against the same state directory, but invoked the model again instead of returning `ANALYSIS_CACHE_HIT`.

The cause was cache eligibility tied to the **whole working-tree Git fingerprint**. A large unrelated uncommitted diff made that fingerprint incomplete. Phase 03 had already correctly narrowed evidence to the explicit `shipping.py` target, but cache read/write still used the broader incomplete fingerprint and were skipped.

## Correction

- Explicit-file requests now derive a scoped cache fingerprint from the named file path and exact collected file content hash.
- A complete explicit evidence scope remains cache-eligible even when unrelated broad diffs are truncated.
- Generic, non-explicit requests retain the original complete-Git-fingerprint cache rule.
- Cache-hit results preserve `model_id`, runtime profile version, and prompt schema version.

## Safety

This does not allow cache reuse across changed explicit file contents: the evidence-bundle hash and scoped fingerprint both change when the target file changes. It does not enable caching for truncated explicit target content.

## Acceptance criteria

1. Explicit-scope Gate A remains `ANALYSIS_COMPLETED`.
2. Same request + same state produces `ANALYSIS_CACHE_HIT` without a model call.
3. Cache artifacts retain actual model identity.
4. Generic diff-scoped requests remain subject to the original repository-fingerprint completeness rule.
