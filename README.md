# Storefront Change Guard

> Local-first, evidence-based assistance for reviewing e-commerce code changes.

## Project status

**Current phase:** Phase 01 — Demo storefront preparation complete.

The prototype is intentionally being built in phases. Phase 01 has established a clean storefront baseline with lint, build, and test checks. The checkout shipping domain and boundary-rule tests are in place for the controlled regression scenario. The review agent implementation is not yet started.

## Challenge objective

This repository contains a focused prototype for a development team that maintains e-commerce storefronts. The system will support change review through an auditable local-first workflow:

```text
Candidate change / branch
        ↓
Deterministic checks and scoped repository context
        ↓
Evidence-based review findings
        ↓
Suggested patch (never applied to the original branch)
        ↓
Isolated validation in a temporary Git worktree
        ↓
Readiness decision with explicit policy rules
```

## Selected capabilities

The technical challenge requests at least two capabilities. This prototype is designed around three connected capabilities, with the first two being the primary commitment:

1. **Review code changes and provide useful, actionable feedback.**
2. **Detect a defect, propose a correction, and validate that correction.**
3. **Decide whether a change is ready to move forward using explicit, auditable criteria.**

Answering ad-hoc questions about code or documentation may be added later as a non-core extension. It is not required for the initial demonstration.

## Design principles and priority order

The system is designed according to the following priority order:

1. **Operability** — another developer should be able to clone, configure, run, and understand the system from the documentation.
2. **Privacy** — source code and review context remain local by default; model access is configured through a local or self-hosted OpenAI-compatible endpoint.
3. **Response time** — the system scopes context to the changed files, directly related code, relevant tests, documentation, and deterministic check output.
4. **Cost** — no paid inference provider is required for the default design.

## Safety and validation boundaries

The prototype will not give an LLM unrestricted authority over the repository.

- The model may analyze supplied context and propose findings or a unified diff.
- The original candidate branch is never modified automatically.
- Any proposed patch is applied only in a temporary Git worktree.
- Tests, linting, build checks, and Git integrity checks are executed by controlled deterministic commands.
- A model cannot claim a check passed; the report must contain the real command output and exit status.
- Findings require repository evidence such as file paths, line references, and matching code excerpts.
- Readiness decisions are driven by policy rules; model reasoning can explain a decision but cannot override hard quality gates.

## Repository layout

```text
storefront-change-guard/
├── README.md                         # This project overview and operating guide
├── .editorconfig                     # Consistent formatting defaults
├── .env.example                      # Local runtime configuration contract
├── .gitignore                        # Excludes secrets, runtime files, worktrees, and dependencies
├── pyproject.toml                    # Python package and development configuration
│
├── agent_solution/                   # The Python review-agent implementation
│   ├── cli.py                         # Current minimal CLI entry point
│   ├── core/                          # Shared configuration, models, paths, and contracts
│   ├── git_tools/                     # Git diff, worktree, and patch operations (planned)
│   ├── checks/                        # Controlled deterministic checks (planned)
│   ├── intelligence/                  # Local-model integration and evidence validation (planned)
│   ├── decision/                      # Policy and readiness-gate logic (planned)
│   ├── reporting/                     # Artifact generation (planned)
│   └── tests/                         # Unit and integration tests
│
├── demo-storefront/                  # Open-source e-commerce scenario and controlled changes
│   ├── UPSTREAM.md                    # Attribution and controlled-modification disclosure
│   ├── docs/checkout-rules.md         # Shipping boundary-rule documentation
│   └── src/domain/checkout/           # Integer-cent shipping domain module
│
├── policies/                         # Explicit machine-readable quality policies
│   └── storefront_policy.yaml
│
├── artifacts/                        # Runtime outputs from the prototype; ignored except .gitkeep
│
├── docs/                             # Human-facing design and delivery documentation
│   ├── architecture.md
│   ├── decisions.md
│   ├── demo-scenarios.md
│   ├── local-model.md
│   ├── threat-model.md
│   └── presentation-outline.md
│
├── AUDIT/                            # Phase-based engineering audits
│   ├── README.md
│   └── phase-00-repository-baseline.md
│
└── REPORT/                           # Execution records, prompt traceability, and change history
    ├── README.md
    ├── ai-usage/
    ├── changelog/
    ├── executions/
    ├── prompts/
    └── templates/
```

## Evidence model: `AUDIT`, `REPORT`, and `artifacts`

These folders have intentionally different roles. Keeping them separate makes the development process and final demo easier to audit.

| Location | What belongs there | Why it exists |
|---|---|---|
| `AUDIT/` | Phase-level engineering records: scope, decisions, risks, implementation summary, validation commands, known limitations, and exit criteria. | Shows how the project evolved and why technical decisions were made. |
| `REPORT/` | Prompt records, tool/model usage traceability, execution reports, changelog entries, and decision logs. | Preserves reproducible evidence of what was run and how AI assistance was used. |
| `artifacts/` | Runtime output produced by the prototype, such as `review.md`, `findings.json`, `proposed-fix.diff`, `validation.json`, and `decision.json`. | Contains the actual product output from a review execution. |

**Rule of thumb:**

- `AUDIT` explains **how the project evolved**.
- `REPORT` explains **what was executed and what assistance was used**.
- `artifacts` contains **what the system produced**.

## Current setup

### Prerequisites

- Windows 10/11 or another supported development environment.
- Python 3.11 or newer.
- Git.
- Node.js and the package manager required by `demo-storefront`.
- A local OpenAI-compatible model endpoint will be required in a later phase. It is not required for the current bootstrap CLI.

### Initial bootstrap

From the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m agent_solution --help
```

The current CLI is only a scaffold. The commands above verify that the Python package is installable and runnable before implementation begins.

### Local configuration

Copy `.env.example` to `.env` before a phase requires local model integration:

```powershell
Copy-Item .env.example .env
```

Do not commit `.env`, credentials, local model paths, or generated runtime artifacts.

## Controlled storefront scenario

The `demo-storefront` folder contains a public open-source storefront used as a controlled scenario. The upstream repository's license and attribution must remain preserved.

Any defects added for the challenge will be introduced intentionally in documented candidate changes. They must never be described as defects discovered in the upstream project unless independent evidence supports that claim.

The initial target scenario is a checkout rule boundary regression:

> Free shipping applies when the cart subtotal is **equal to or greater than** a configured threshold.

The candidate change will intentionally use an incorrect strict comparison so that the review system can detect, explain, propose, and validate the correction.

## Planned output contract

Once implemented, each review run should produce a directory under `artifacts/` containing at least:

```text
artifacts/<run-id>/
├── review.md
├── findings.json
├── proposed-fix.diff
├── validation.json
├── decision.json
└── run-metadata.json
```

The exact contract may evolve, but artifacts must remain machine-readable where appropriate and linked to the candidate change, executed commands, policy version, and model configuration.

## Development milestones

| Phase | Goal | Primary evidence |
|---|---|---|
| Phase 00 | Establish the demo storefront baseline before any modifications. | `AUDIT/phase-00-repository-baseline.md` |
| Phase 01 | Prepare documented checkout rules, tests, and controlled candidate changes. | Phase audit + storefront commits | ✅ |
| Phase 02 | Implement Git context collection and deterministic checks. | CLI and automated tests |
| Phase 03 | Add local-model review with structured output and evidence validation. | Review artifacts + tests |
| Phase 04 | Add isolated patch application and validation worktrees. | Validation artifacts + integration tests |
| Phase 05 | Add policy-driven readiness decisions and end-to-end runs. | Decision artifacts + scenario report |
| Phase 06 | Final reproducibility, documentation, rehearsal, and delivery review. | Delivery-readiness audit |

## AI usage and ownership

AI-assisted tools may be used for exploration, drafting, implementation support, review, and documentation improvement. They are treated as engineering aids, not as autonomous authorities.

The author retains ownership of the project scope, architecture, privacy boundary, evaluation criteria, controlled scenarios, integration choices, validation strategy, final review, debugging, and delivery. See `REPORT/ai-usage/AI_USAGE_DISCLOSURE.md` for the project disclosure and `REPORT/prompts/` for prompt records that are intentionally retained.

## Documentation index

- `docs/architecture.md` — architecture direction and boundaries.
- `docs/decisions.md` — decision log and alternatives.
- `docs/demo-scenarios.md` — controlled scenario design.
- `docs/local-model.md` — local inference and configuration strategy.
- `docs/threat-model.md` — privacy, safety, and trust boundaries.
- `docs/presentation-outline.md` — live-demo structure.
- `AUDIT/README.md` — audit record convention.
- `REPORT/README.md` — report and prompt traceability convention.

## License and upstream attribution

The root prototype is being prepared for technical-challenge evaluation. The `demo-storefront` retains its upstream license and attribution. See `demo-storefront/UPSTREAM.md` and preserve any upstream `LICENSE` file already present in the cloned project.
