# Test 1 — Broad Local Model and Quantization Comparison

**Project:** Storefront Change Guard  
**Run ID:** `model-selection-final-20260624`  
**Execution date:** 2026-06-24  
**Status:** Completed successfully; human quality review remains pending  
**Scope:** Four local Qwen3.5 GGUF candidates on the target Windows workstation  
**Purpose:** Establish local viability, broad performance, memory behavior, deterministic stability, and finalists for the controlled Test 2 latency study.

> **Decision status:** This report is a complete performance and operability record, not a final semantic-quality verdict. The 16 quality-smoke outputs are indexed for manual review under [`quality_review/`](quality_review/). Finalist selection for Test 2 should combine these measured results with that review.

---

## 1. Executive Summary

Test 1 compared two Qwen3.5 model sizes (4B and 9B) at two quantization levels (UD-Q4_K_XL and UD-IQ3_XXS) using a fixed long-context local runtime configuration. The campaign completed without model crashes, timeouts, interrupted units, or missing raw output references.

The strongest **verified** findings are:

- All four candidates completed the entire broad suite successfully.
- **Qwen3.5-4B UD-IQ3_XXS** had the highest median cold generation throughput at **63.1 tokens/s** and the lowest median RSS at **2.06 GiB**.
- **Qwen3.5-4B UD-Q4_K_XL** had the highest median cold prompt throughput at **320.0 tokens/s** and a materially lower memory footprint than either 9B candidate.
- **Qwen3.5-9B UD-IQ3_XXS** remained operationally viable on the workstation, using **3.59 GiB** median RSS and reaching **39.4 tokens/s** median cold generation throughput.
- **Qwen3.5-9B UD-Q4_K_XL** had the largest memory footprint at **5.28 GiB** median RSS and the lowest median generation throughput at **33.5 tokens/s**.
- The warm, server-loaded sessions completed for all candidates. Their request-wall-clock measurements are operationally useful, but they are not directly comparable to cold CLI throughput and are reported separately.

The performance-only ranking is therefore:

1. Qwen3.5-4B UD-IQ3_XXS — throughput and memory leader.
2. Qwen3.5-4B UD-Q4_K_XL — higher-precision 4B alternative with stronger prompt throughput.
3. Qwen3.5-9B UD-IQ3_XXS — viable larger-model candidate; retains a reasonable memory footprint for 9B.
4. Qwen3.5-9B UD-Q4_K_XL — viable but heaviest and slowest candidate in this setup.

This ranking is **not** a claim that the first candidate is semantically best. The quality-smoke review is the remaining decision gate.

---

## 2. Decision Question

> Which locally runnable Qwen3.5 GGUF candidate gives Storefront Change Guard the best balance of speed, memory efficiency, operational stability, and evidence-grounded response quality on the target workstation?

Test 1 answers the **viability and broad performance** part of that question. It does not replace human evaluation of grounded output quality.

---

## 3. Target Environment

| Component | Recorded value |
|---|---|
| Operating system | Windows 10, build `10.0.26200` |
| CPU | AMD Ryzen 5 8500G, 6 cores / 12 logical processors |
| GPU | AMD Radeon RX 6600 8GB|
| GPU driver | `32.0.21043.19003` |
| Installed RAM | 16,800,985,088 bytes / approximately 15.65 GiB |
| Python | 3.11.9 |
| llama.cpp | version 791 (`c1304d7`), MSVC x64 build |
| GPU offload | `-ngl auto` |
| GPU VRAM telemetry | Not available; CPU process RSS is the measured memory metric |

**Important limitation:** RSS is host-process memory. It is not VRAM usage, and model file size is not VRAM usage.

---

## 4. Fixed Runtime Configuration

All benchmark candidates used the same primary runtime profile:

```text
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
```

Additional cold CLI behavior used the model-supported Jinja template plus non-interactive output control:

```text
--jinja
--no-display-prompt
-st
```

### Interpretation note

`-n 8192` was the broad-benchmark completion ceiling. It is **not** the planned production response budget for Storefront Change Guard. Test 2 will use controlled completion budgets and a fixed prompt packet to characterize p50/p95/p99 latency cleanly.

---

## 5. Candidate Identity and Reproducibility

| Candidate | Family | Quantization | GGUF size (GiB) | SHA-256 prefix |
|---|---|---:|---:|---|
| `qwen35_4b_ud_q4_k_xl` | Qwen3.5-4B | UD-Q4_K_XL | 2.71 | `b252c5610a42ca82` |
| `qwen35_4b_ud_iq3_xxs` | Qwen3.5-4B | UD-IQ3_XXS | 1.82 | `00aab66a2359a9af` |
| `qwen35_9b_ud_q4_k_xl` | Qwen3.5-9B | UD-Q4_K_XL | 5.56 | `6f5d30666c2d8ae1` |
| `qwen35_9b_ud_iq3_xxs` | Qwen3.5-9B | UD-IQ3_XXS | 3.74 | `40d0f32cd3030b04` |

The immutable source `events.jsonl` used for this package has SHA-256 prefix:

```text
b1a272208e9a4d99...
```

Supporting analysis summaries and the original source manifest are preserved under [`data/`](data/).

---

## 6. Campaign Timing

### 6.1 Measurement window

| Timing measure | Value | Provenance |
|---|---:|---|
| First recorded event | `2026-06-24T05:11:29.543952+00:00` | metadata collection event |
| Last recorded benchmark event | `2026-06-24T07:54:59.499823+00:00` | final quality-smoke completion |
| Campaign elapsed time | **2h 43m 29.96s** | first-to-last event timestamp |
| Sum of measured cold CLI wall time | 1h 26m 26.89s | 84 cold unit `wall_seconds` values |
| Sum of measured quality-smoke wall time | 0h 21m 39.17s | 16 quality unit `wall_seconds` values |
| Sum of warm server request wall time | 0h 54m 45.06s | 56 request `wall_seconds` values |
| Sum of all direct model work records | **2h 42m 51.11s** | cold + quality + warm request values |
| Approximate orchestration gap | **38.84 s** | campaign elapsed minus direct work sum |

The warm server-session lifecycle durations are **not added** to the direct-work total because their request events occur inside those server session windows; adding both would double count time.

---

## 7. Measurement Inventory

The run completed **108 benchmark units**:

- **84 cold CLI units:** 4 models × 7 prompts × 3 repetitions.
- **8 server-loaded sessions:** 2 sessions per model.
- **16 quality-smoke units:** 4 models × 4 evidence-grounded prompts.

The event log contains **165 events**, including:

| Event type | Count | What it represents |
|---|---:|---|
| `benchmark_unit` | 100 | 84 cold CLI executions + 16 quality-smoke executions |
| `warm_turn` | 56 | individual HTTP requests served by llama-server |
| `server_session` | 8 | server lifecycle records; 2 per model |
| `metadata_collection` | 1 | environment and GGUF identity capture |

This yields **156 direct model measurements**: 84 cold CLI + 56 warm server requests + 16 quality outputs.

All 164 executable/model-related events recorded a `success` status. No failures, timeouts, interruptions, or unsupported events were recorded. All raw paths referenced by successful events were verified as present.

---

## 8. Benchmark Workloads

### 8.1 Cold CLI suite

Each cold unit loaded a fresh model process, submitted one prompt, recorded raw stdout/stderr, parsed CLI throughput when emitted, captured wall-clock duration and process-tree RSS, and exited.

Prompts:

| Prompt ID | Language | Category |
|---|---|---|
| `warmup_gpu_en` | English | Warm-up explanation |
| `train_es` | Spanish | Quantitative reasoning |
| `scraper_es` | Spanish | Python code generation |
| `startup_plan_es` | Spanish | Structured planning |
| `train_en` | English | Quantitative reasoning |
| `scraper_en` | English | Python code generation |
| `startup_plan_en` | English | Structured planning |

### 8.2 Warm server-loaded suite

Each model was loaded into `llama-server` locally on `127.0.0.1`, then served seven sequential requests per session. Two sessions were executed per model.

These metrics are reported as **server request wall-clock durations**, not as CLI token throughput. They are operationally meaningful but must not be averaged with cold CLI throughput.

### 8.3 Quality-smoke suite

Each candidate produced four evidence-grounded outputs:

- `verified_shipping_rule`
- `inferred_scope`
- `unknown_approval`
- `anti_hallucination_review`

The outputs were indexed and preserved for human review. No subjective scores were assigned automatically.

---

## 9. Cold CLI Performance Summary

| Model | GGUF size (GiB) | Gen. t/s p50 | Gen. t/s p05–p95 | Gen. CV | Prompt t/s p50 | RSS p50 (GiB) | Wall p50 (s) | Wall mean (s) | n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5-4B UD-Q4_K_XL | 2.71 | 54.1 | 52.8–54.7 | 1.13% | 320.0 | 2.96 | 50.8 | 65.1 | 21 |
| Qwen3.5-4B UD-IQ3_XXS | 1.82 | 63.1 | 61.4–64.1 | 1.46% | 259.6 | 2.06 | 44.0 | 56.7 | 21 |
| Qwen3.5-9B UD-Q4_K_XL | 5.56 | 33.5 | 33.3–33.7 | 0.41% | 206.3 | 5.28 | 69.1 | 67.4 | 21 |
| Qwen3.5-9B UD-IQ3_XXS | 3.74 | 39.4 | 39.1–39.6 | 0.44% | 156.7 | 3.59 | 60.9 | 57.8 | 21 |

### How to read this table

- **Generation t/s** is the CLI-reported completion throughput.
- **Prompt t/s** is the CLI-reported prompt-evaluation throughput.
- **RSS** is peak process-tree resident memory; it is not VRAM.
- **Wall time** includes process launch, model load, context allocation, prompt evaluation, response generation, and shutdown.
- The sample count is 21 cold observations per candidate: 7 heterogeneous prompts × 3 repetitions.
- p99 is deliberately not reported because 21 heterogeneous observations per model are insufficient for a defensible p99 estimate.

---

## 10. Quantization Trade-offs Observed

### Qwen3.5-4B: UD-IQ3_XXS vs UD-Q4_K_XL

| Metric | Observed change when using IQ3_XXS |
|---|---:|
| Median generation throughput | **+16.6%** |
| GGUF file size | **-32.8%** |
| Median RSS | **-30.4%** |
| Median prompt throughput | **-18.9%** |

### Qwen3.5-9B: UD-IQ3_XXS vs UD-Q4_K_XL

| Metric | Observed change when using IQ3_XXS |
|---|---:|
| Median generation throughput | **+17.6%** |
| GGUF file size | **-32.7%** |
| Median RSS | **-32.0%** |
| Median prompt throughput | **-24.0%** |

**Verified interpretation:** In this environment, IQ3_XXS improved completion throughput and reduced host memory/file size within both model families, while Q4_K_XL retained higher median prompt throughput. Whether that quality/speed trade-off is appropriate for Change Guard remains a human quality-review question.

---

## 11. Cold Wall-Time Detail by Prompt

Median wall-clock duration in seconds. Each cell summarizes three fresh-process cold runs.

| Prompt | 4B Q4_K_XL | 4B IQ3_XXS | 9B Q4_K_XL | 9B IQ3_XXS |
|---|---:|---:|---:|---:|
| `warmup_gpu_en` | 27.4 | 16.9 | 35.6 | 38.7 |
| `train_es` | 83.5 | 70.9 | 84.6 | 93.7 |
| `scraper_es` | 27.6 | 25.7 | 34.0 | 22.4 |
| `startup_plan_es` | 158.6 | 136.4 | 88.3 | 84.2 |
| `train_en` | 89.4 | 89.7 | 136.4 | 80.9 |
| `scraper_en` | 17.9 | 12.6 | 23.4 | 23.7 |
| `startup_plan_en` | 50.8 | 44.0 | 69.1 | 60.9 |

### Interpretation

The heterogeneous suite intentionally produces different output lengths and reasoning behaviors. Therefore:

- a lower overall p50 does not prove a model is universally faster;
- prompt-specific differences must not be interpreted as pure inference-speed differences;
- Test 2 will use one fixed prompt packet with bounded output budgets to isolate comparable tail-latency behavior.

---

## 12. Warm Server-Loaded Sequential Results

| Model | Sessions | Requests | Startup p50 (s) | Request wall p50 (s) | Request wall mean (s) | Request range (s) | Session total p50 (s) | Completion tokens reported |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5-4B UD-Q4_K_XL | 2 | 14 | 4.10 | 48.17 | 36.47 | 9.81–61.01 | 259.94 | 27556 |
| Qwen3.5-4B UD-IQ3_XXS | 2 | 14 | 3.03 | 56.08 | 62.96 | 4.33–133.90 | 444.14 | 54240 |
| Qwen3.5-9B UD-Q4_K_XL | 2 | 14 | 5.55 | 59.99 | 52.07 | 9.97–89.82 | 370.77 | 24250 |
| Qwen3.5-9B UD-IQ3_XXS | 2 | 14 | 4.05 | 46.85 | 83.16 | 8.70–213.22 | 586.80 | 44880 |

### Important provenance rule

- Warm request duration is a client-observed HTTP request wall-clock measurement.
- It is **not** generation throughput.
- Server startup is separate from request latency.
- No persistent KV-cache reuse is claimed beyond the observed loaded-server session behavior.

---

## 13. Stability, Memory, and Outliers

### Stability

- Cold CLI: 84/84 successful.
- Warm server turns: 56/56 successful.
- Quality smoke: 16/16 successful.
- No recorded timeout, crash, interrupt, or missing raw-output reference.

### Memory

The measured median RSS range was:

```text
2.06 GiB  →  5.28 GiB
```

All candidates remained within the available system memory envelope during this campaign.

### Outlier policy and result

The analysis inspected 336 metric observations. Because relevant comparison groups were small, the analysis correctly classified all observations as:

```text
small-n visual inspection only
```

No potential or robust statistical outliers were asserted, and no sample was removed from any report or chart.

---

## 14. Quality Review Status

The quality-smoke outputs exist, but **semantic quality is not automatically scored**.

Manual review material is included under [`quality_review/`](quality_review/):

- [`quality-review-guide.md`](quality_review/quality-review-guide.md)
- [`quality-review-template.csv`](quality_review/quality-review-template.csv)
- [`quality-smoke-output-index.md`](quality_review/quality-smoke-output-index.md)
- [`quality-smoke-output-index.csv`](quality_review/quality-smoke-output-index.csv)

The rubric scores each candidate output from 0 to 2 for:

1. correctness;
2. evidence accuracy;
3. answer-type behavior (`VERIFIED`, `INFERRED`, `UNKNOWN`);
4. language quality;
5. limitations honesty.

### Current selection status

| Claim | Status |
|---|---|
| 4B IQ3_XXS is the performance and memory leader | **VERIFIED** |
| 4B Q4_K_XL is the higher-precision 4B alternative | **VERIFIED** |
| 9B IQ3_XXS is operationally viable on the target machine | **VERIFIED** |
| Any candidate is semantically best for Change Guard | **UNKNOWN until human quality review** |
| Finalists for Test 2 | **AWAITING_HUMAN_QUALITY_REVIEW** |

---

## 15. What Test 1 Proves — and Does Not Prove

### VERIFIED

- All four candidates complete the test suite on this workstation.
- The full 108-unit campaign completed without runtime failures.
- 4B variants generated faster than 9B variants under the cold CLI profile.
- IQ3_XXS variants generated faster and used less measured RSS than Q4_K_XL within the same model family.
- Warm server-loaded sequential sessions were viable for all candidates.
- Raw outputs, event records, model hashes, and report artifacts were preserved.

### INFERRED

- The 4B candidates are likely better fits where speed and memory efficiency dominate.
- The 9B IQ3 candidate may remain competitive when human quality review demonstrates a meaningful improvement.
- A Test 2 controlled-latency campaign is warranted for two finalists rather than all four candidates.

### UNKNOWN

- Which candidate produces the best grounded review quality.
- Whether Q4 precision has a meaningful practical advantage for this agent.
- GPU VRAM use and GPU-only bottlenecks.
- Production latency under the smaller per-operation output budgets planned for Change Guard.

---

## 16. Recommended Next Step: Test 2

Test 2 should select two candidates only after the manual quality review.

It should use:

```text
2 finalists
× 3 completion-budget conditions
× 100 successful comparable cold samples per group
```

Recommended controlled conditions:

| Condition | Completion budget | What it isolates |
|---|---:|---|
| `prefill_only` | `-n 0` | prompt evaluation plus cold process overhead |
| `bounded_512` | `-n 512` | prompt evaluation plus a bounded normal answer |
| `bounded_1024` | `-n 1024` | prompt evaluation plus a bounded complete response |

Test 2 must keep the prompt packet fixed across conditions, interleave models with a recorded schedule seed, preserve failures, and calculate p50/p95/p99 only after each exact group reaches 100 successful comparable samples.

---

## 17. Plot Gallery

All PNG plots are preserved under [`plots/`](plots/). No samples were intentionally excluded.

### Cold Cli Generation Throughput Distribution

![cold_cli_generation_throughput_distribution](plots/cold_cli_generation_throughput_distribution.png)

### Cold Cli Generation Throughput Variability

![cold_cli_generation_throughput_variability](plots/cold_cli_generation_throughput_variability.png)

### Cold Cli Model Size Vs Generation Throughput

![cold_cli_model_size_vs_generation_throughput](plots/cold_cli_model_size_vs_generation_throughput.png)

### Cold Cli Peak Memory Distribution

![cold_cli_peak_memory_distribution](plots/cold_cli_peak_memory_distribution.png)

### Cold Cli Prompt Throughput Distribution

![cold_cli_prompt_throughput_distribution](plots/cold_cli_prompt_throughput_distribution.png)

### Cold Cli Prompt Vs Generation Throughput

![cold_cli_prompt_vs_generation_throughput](plots/cold_cli_prompt_vs_generation_throughput.png)

### Cold Cli Success And Failure Summary

![cold_cli_success_and_failure_summary](plots/cold_cli_success_and_failure_summary.png)

### Cold Cli Wall Time By Prompt

![cold_cli_wall_time_by_prompt](plots/cold_cli_wall_time_by_prompt.png)

### Cold Vs Server Metric Provenance

![cold_vs_server_metric_provenance](plots/cold_vs_server_metric_provenance.png)

### Server Sequential Request Wall Time By Turn

![server_sequential_request_wall_time_by_turn](plots/server_sequential_request_wall_time_by_turn.png)

### Server Sequential Session Total Duration

![server_sequential_session_total_duration](plots/server_sequential_session_total_duration.png)

### Server Startup And Health Latency

![server_startup_and_health_latency](plots/server_startup_and_health_latency.png)

---

## 18. Included Package Contents

```text
benchmark_results/
└── test_1/
    ├── README.md
    ├── data/
    │   ├── model-summary.csv
    │   ├── model-summary.json
    │   ├── prompt-summary.csv
    │   ├── prompt-summary.json
    │   ├── outlier-analysis.csv
    │   ├── outlier-analysis.json
    │   ├── evidence-inventory.md
    │   └── source-analysis-manifest.md
    ├── quality_review/
    │   ├── quality-review-guide.md
    │   ├── quality-review-template.csv
    │   ├── quality-smoke-output-index.csv
    │   └── quality-smoke-output-index.md
    └── plots/
        └── 12 PNG charts
```

The execution harness, raw runtime logs, model files, and source code are intentionally excluded from this presentation package. They remain in the local project as source evidence.

---
