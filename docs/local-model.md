# Local Model Strategy — Initial Direction

## Objective

Use a local-first model through an OpenAI-compatible API interface so sensitive repository content remains within the developer-controlled environment by default.

## Why not require a large model

The prototype will keep the model task narrow:

- inspect a bounded diff;
- compare it with directly relevant source, tests, and documentation;
- produce structured findings;
- propose a small unified diff when justified.

Reliability comes from constrained context, deterministic checks, evidence validation, and policy gates—not from depending on a very large model for every decision.

## Configuration contract

The model endpoint and name are configured through `.env` and are intentionally not hard-coded. A later implementation phase will support a local endpoint such as `llama-server` or another compatible local service.

## Privacy boundary

- Default model access is local.
- Remote model use is disabled by default.
- No credential or source-code content is written to prompt records by default.
- Runtime reports must redact secrets and environment values.

## Pending selection criteria

The final model will be selected after baseline measurements using:

- structured-output reliability;
- ability to reason about small TypeScript/React changes;
- response time on the local hardware;
- RAM/VRAM requirements;
- ease of reproducible setup.
