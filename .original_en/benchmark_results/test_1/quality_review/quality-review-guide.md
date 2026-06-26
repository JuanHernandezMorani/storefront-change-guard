# Quality Review Guide

## Purpose

This guide explains how to manually review the quality smoke outputs for each model. No automated quality scoring is performed — all quality assessment requires human judgment.

## Scoring Rubric

Each dimension is scored 0-2:

| Score | Meaning |
|-------|---------|
| 0 | Fails completely |
| 1 | Partially acceptable |
| 2 | Fully acceptable |

### Dimensions

1. **Correctness (0-2):** Is the response factually accurate and logically sound?
2. **Evidence accuracy (0-2):** Does the response reference correct sources/data?
3. **Answer type accuracy (0-2):** Does the response match the expected answer type (VERIFIED, INFERRED, UNKNOWN)?
4. **Language quality (0-2):** Is the response well-written and clear?
5. **Limitations honesty (0-2):** Does the response acknowledge uncertainty when appropriate?

**Total: 0-10 per output**

## Instructions

1. Open each quality output in `raw/` directory
2. For each model-prompt pair, read the output
3. Check deterministic fixtures (output exists, expected label present)
4. Score each dimension using the rubric
5. Add reviewer notes
6. Enter scores in the `quality-review-template.csv`

## Expected Answer Types

- **VERIFIED:** The model should confirm a verifiable fact
- **INFERRED:** The model should draw a reasonable inference
- **UNKNOWN:** The model should acknowledge uncertainty
- **VERIFIED_OR_NO_FINDING:** The model should verify or report no finding

## Important

- Do not assign scores based on speed or memory — only output quality matters
- Consider bilingual capability (English and Spanish prompts)
- Note if the model hallucinates facts
- Note if the model refuses to answer when it should answer
