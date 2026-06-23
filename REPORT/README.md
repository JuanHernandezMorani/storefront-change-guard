# Reports and AI Usage Traceability

This directory contains execution reports, prompt records, decision logs, and AI-assisted development disclosures.

The project may use AI as an engineering aid for exploration, drafting, review, and iteration. Final architectural decisions, acceptance criteria, validation strategy, integration, testing, debugging, and delivery ownership remain with the author.

## Directory responsibilities

| Directory | Content |
|---|---|
| `prompts/` | Selected prompt records that materially influenced implementation or design. |
| `executions/` | Human-readable summaries and machine-readable outputs from named review runs. |
| `changelog/` | Change history and material decision notes. |
| `ai-usage/` | High-level disclosure of AI-assisted work. |
| `templates/` | Reusable templates for consistent records. |

## Rules

- Do not commit secrets, API keys, private source code dumps, local paths that are sensitive, or raw chat transcripts by default.
- Retain enough information to explain a prompt's purpose, tool/model used, output disposition, and resulting implementation decision.
- Prefer a concise normalized record over a large unfiltered transcript.
- Use stable identifiers such as `prompt-001` and `run-001`.
- Keep generated runtime product artifacts under `artifacts/`, not here.
