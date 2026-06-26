# Run 015 — Phase 03 Live Gates

## Purpose

Record the completed live validation sequence for evidence-grounded analysis,
cache behavior, Spanish file-scoped Q&A, and safe insufficient-evidence
handling.

## Runtime

- Selected local model: `Qwen3.5-9B-UD-IQ3_XXS.gguf`
- Runtime identity: `qwen3.5-9b-ud-iq3-xxs`
- Runner: `scripts/run_phase03_live_gates.ps1`
- Artifact root at execution: `C:\Users\braia\AppData\Local\Temp\storefront-change-guard-phase03-live-gates-20260626-031530`

## Results

| Gate | Request | Expected status | Recorded result |
|---|---|---|---|
| A | `Review shipping.py.` | `ANALYSIS_COMPLETED` | Pass; cache miss; selected model identity |
| B | Exact repeat of Gate A using same state | `ANALYSIS_CACHE_HIT` | Pass; cache hit; selected model identity |
| C | `Que hace calculate_shipping en shipping.py?` with `es` language | `ANALYSIS_COMPLETED` | Pass; selected model identity |
| D | `Review definitely_missing_shipping_file.py.` | `INSUFFICIENT_EVIDENCE` | Pass; no model identity emitted |

## Notes

- Gate C uses ASCII Spanish deliberately so the runner remains compatible with
  Windows PowerShell legacy file decoding paths.
- Gate D exercises the safe no-evidence path rather than requesting speculative
  analysis.
- Raw model reasoning and raw runtime transcripts are not retained in this
  record.
- The canonical Gate A JSON consumed by Phase 05 is retained as
  `artifacts/phase05-live/run-20260626-033155/inputs/phase03-analysis.utf8.json`.
