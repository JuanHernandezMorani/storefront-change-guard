# Evidence Inventory

**Run ID:** `model-selection-final-20260624`
**Generated:** 2026-06-24T14:15:21.014384Z

## Totals
- Total events: **165**
- Completed units: **108 / 108**
- Raw output files: **272**
- All raw paths from successful events exist: **True**

## Event counts by event_type
- `benchmark_unit`: 100
- `metadata_collection`: 1
- `server_session`: 8
- `warm_turn`: 56

## Benchmark unit counts by mode
- `cold`: 84
- `quality_smoke`: 16

## Counts by model
- `qwen35_4b_ud_iq3_xxs`: 39
- `qwen35_4b_ud_q4_k_xl`: 39
- `qwen35_9b_ud_iq3_xxs`: 39
- `qwen35_9b_ud_q4_k_xl`: 39

## Counts by model family
- `Qwen3.5-4B`: 78
- `Qwen3.5-9B`: 78

## Counts by quantization
- `UD-IQ3_XXS`: 78
- `UD-Q4_K_XL`: 78

## Counts by prompt
- `anti_hallucination_review`: 4
- `inferred_scope`: 4
- `scraper_en`: 20
- `scraper_es`: 20
- `startup_plan_en`: 20
- `startup_plan_es`: 20
- `train_en`: 20
- `train_es`: 20
- `unknown_approval`: 4
- `verified_shipping_rule`: 4
- `warmup_gpu_en`: 20

## Status counts
- `success`: 164

## Success / Failure / Timeout / Interrupted
- Successful: 164
- Failed: 0
- Timeout: 0
- Interrupted: 0
- Unsupported: 0

## Metric provenance labels present
- `cli_reported_generation_tps`: 16
- `server_request_wall_clock_seconds`: 56

## Server-loaded sequential sessions
- Sessions: 8
- Total request measurements: 56
  - `warm__qwen35_4b_ud_q4_k_xl__session01`: 7 turns
  - `warm__qwen35_4b_ud_q4_k_xl__session02`: 7 turns
  - `warm__qwen35_4b_ud_iq3_xxs__session01`: 7 turns
  - `warm__qwen35_4b_ud_iq3_xxs__session02`: 7 turns
  - `warm__qwen35_9b_ud_q4_k_xl__session01`: 7 turns
  - `warm__qwen35_9b_ud_q4_k_xl__session02`: 7 turns
  - `warm__qwen35_9b_ud_iq3_xxs__session01`: 7 turns
  - `warm__qwen35_9b_ud_iq3_xxs__session02`: 7 turns

## Missing raw paths
None - all paths verified.