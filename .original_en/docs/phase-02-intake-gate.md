# Phase 2 — Request Intake and Prompt Quality Gate

## Purpose

The Request Intake and Prompt Quality Gate prevents the agent from treating vague, underspecified, unsafe, or unsupported requests as fully actionable instructions.  It improves requests only through explicit, traceable assumptions and structured execution contracts.  It never silently invents missing facts.

## Decision Matrix

| Condition | Decision |
|---|---|
| Request is well-specified with all required evidence present | `ACCEPT_AS_IS` |
| Request is actionable using a documented low-risk repository default | `ACCEPT_WITH_SAFE_DEFAULTS` |
| Request is understandable but needs structured reformulation | `REFINE_FOR_EXECUTION` |
| Request is materially underspecified or unsafe | `CLARIFY` |
| Request is out of supported scope or violates safety policy | `REJECT_UNSAFE_OR_UNSUPPORTED` |

### Fail-closed rules

- `UNKNOWN` task type → always `CLARIFY`
- `LOW` classification confidence → always `CLARIFY`
- Missing required evidence → `CLARIFY` (never fabricate)
- `HIGH` or `CRITICAL` risk → `CLARIFY` or `REJECT`
- Mixed unrelated goals → `CLARIFY` with decomposition request
- Security/production claims without evidence → `CLARIFY` or `REJECT`

## Task Types

| Type | Description | Safe defaults |
|---|---|---|
| `CODE_REVIEW` | Review current changes or specified files | Current diff (when available) |
| `BUG_DIAGNOSIS` | Diagnose a reported bug | None (requires evidence) |
| `CODEBASE_QUESTION` | Answer a question about the codebase | Bounded repository search |
| `READINESS_ASSESSMENT` | Assess deployment readiness | None (requires explicit criteria) |
| `PATCH_PROPOSAL` | Propose code changes | None (requires target and criteria) |
| `UNKNOWN` | Cannot classify with confidence | None |

## Safe Defaults

Safe defaults are conservative defaults applied only in LOW-risk scenarios.  Every applied default must be visible in the resulting execution contract.

### CODE_REVIEW

- **Condition:** User asks to review the current change AND a non-empty working-tree diff exists.
- **Default:** Scope = current Git diff (staged + unstaged).
- **Requirement:** The execution contract must explicitly state this scope.
- **Fallback:** When no diff exists → `CLARIFY`.

### CODEBASE_QUESTION

- **Condition:** User asks a codebase question without specifying a path.
- **Default:** Bounded repository search with configurable limits.
- **Requirement:** Search scope and limits must be recorded.
- **Limits:** Max 20 results, max 24,000 context characters.

### BUG_DIAGNOSIS

- **No safe defaults.** Requires observed symptom, error/log, reproduction steps, or expected-vs-actual behavior.

### READINESS_ASSESSMENT

- **No safe defaults.** Requires deployment target, validation criteria, risk tolerance, and environment constraints.

### PATCH_PROPOSAL

- **No safe defaults.** Requires explicit target area and acceptance criteria.
- **Invariant:** Patches apply only in isolated worktrees.
- **Decision rule:** `ACCEPT_WITH_SAFE_DEFAULTS` is never permitted for patch proposals.  A patch request may become `REFINE_FOR_EXECUTION` only when all of the following are explicit: target scope, expected behavior or desired change, constraints (when relevant), and validation criteria or validation command.  Otherwise the decision must be `CLARIFY`.

## Patch Proposal Decision Contract

A patch proposal is a request to modify code.  The intake gate applies a strict conservative policy:

| Condition | Decision |
|---|---|
| All required fields explicit (target, expected behavior, validation) AND high classification confidence | `REFINE_FOR_EXECUTION` |
| Required fields present but classification confidence is LOW | `CLARIFY` |
| Any required field missing (target, expected behavior, or validation) | `CLARIFY` |
| Mixed goals detected (patch + other task types) | `CLARIFY` with decomposition |

**Critical invariant:** No patch request may become directly executable through Phase 2A.  `ACCEPT_WITH_SAFE_DEFAULTS` is never used for `PATCH_PROPOSAL`.  Patch proposals always require an execution brief with explicit worktree-only constraints before any mutation occurs.

### Required fields for REFINE_FOR_EXECUTION

1. **Target scope** — which files or code region should change.
2. **Expected behavior** — what the change should achieve or produce.
3. **Constraints** — what must remain unchanged or what limits apply (when relevant).
4. **Validation criteria** — how success will be verified (test command, expected output, or acceptance checks).

### Examples

**Sufficient for REFINE_FOR_EXECUTION:**

```
Modify src/domain/checkout/shipping.ts to change the boundary from >= to >.
Expected: 599 cents ships free, 600 cents charges shipping.
Validate with: npm test
```

**Insufficient (returns CLARIFY):**

```
Fix the bug.
```

```
Modify the shipping calculation.
```

## Mixed-Goals Detection

The intake gate uses **deterministic task-signal overlap** to detect mixed-goal requests.  A request is mixed-goals when it contains signals from two or more distinct task types requiring different execution contracts or levels of authority.

### Detection mechanism

For each supported task type, the detector checks whether the request text matches at least one pattern from that type's keyword set.  When two or more distinct task types match, the request is classified as mixed-goals.

### Required behavior for mixed goals

When mixed goals are detected:

1. `decision` must be `CLARIFY`.
2. `clarifying_questions` must include a decomposition request explaining that the detected task types have different evidence requirements and execution contracts.
3. `blocking_reasons` must explain why decomposition is required.
4. No default scope or execution authorization is applied.
5. The system must not silently select one task and ignore the others.

### Detected task types for signal overlap

| Task Type | Example signals |
|---|---|
| `CODE_REVIEW` | "review", "check change", "revisá" |
| `BUG_DIAGNOSIS` | "fix bug", "error", "crash", "arreglar" |
| `CODEBASE_QUESTION` | "explain", "how does", "where is", "qué es" |
| `READINESS_ASSESSMENT` | "ready", "production", "deploy", "listo" |
| `PATCH_PROPOSAL` | "patch", "modify", "improve", "refactor", "mejorar" |

### English example

**Request:** "Review the checkout change, fix any issue you find, and tell me whether it is ready for production."

**Detected signals:** `CODE_REVIEW` ("review") + `PATCH_PROPOSAL` ("fix") + `READINESS_ASSESSMENT` ("ready", "production")

**Result:** `CLARIFY` with decomposition request explaining that review, patch proposal, and readiness assessment have different required evidence and execution contracts.

### Spanish example

**Request:** "Revisá el cambio de checkout, corregí cualquier problema y decime si está listo para producción."

**Detected signals:** `CODE_REVIEW` ("revisá") + `PATCH_PROPOSAL` ("corregí") + `READINESS_ASSESSMENT` ("listo", "producción")

**Result:** `CLARIFY` with decomposition request.

## Worktree-Only Invariant

Patch proposals that reach `REFINE_FOR_EXECUTION` carry a mandatory constraint: patches apply only in temporary, isolated worktrees.  This invariant is preserved in the execution brief constraints and enforced by Phase 4 (Isolated Patch Validation).  Phase 2A records the constraint; Phase 4 enforces it.

## Clarification Policy

Clarifying questions are targeted and minimal.  Questions that can be answered from deterministic repository context are NOT generated.

### For bugs

- What behavior did you observe?
- What behavior did you expect?
- Can you provide an error, logs, reproduction steps, or the relevant change?

### For readiness

- Which target environment is being assessed?
- What acceptance checks are required?
- Which risks are blocking versus advisory?

### For patches

- Which files or behavior should change?
- What must remain unchanged?
- How should success be validated?

### For mixed goals

- This request mixes multiple distinct goals (e.g., review, patch proposal, readiness assessment).  Each requires different evidence and execution contracts.  Please decompose into a single primary task per request.

## Refined Execution Brief

When the decision is `REFINE_FOR_EXECUTION`, a structured execution brief is produced.  It must contain:

| Field | Description |
|---|---|
| `goal` | What the request aims to achieve |
| `task_type` | Classified task type |
| `scope` | Deterministic scope from repository state |
| `available_evidence` | Evidence already available |
| `required_evidence` | Evidence needed to proceed |
| `safe_defaults` | Defaults applied (if any) |
| `assumptions` | All explicit assumptions with confidence |
| `constraints` | Hard constraints on execution |
| `expected_output` | What the output must contain |
| `validation_plan` | How output will be validated |
| `stop_conditions` | When execution must stop |

The brief always preserves the original request wording and uncertainty markers.

## Model-Agnostic Routing Contract

Three provisional profile templates support future routing:

| Profile | Role | Allowed types | Escalation |
|---|---|---|---|
| `fast_model_profile` | Fast triage | `CODE_REVIEW`, `CODEBASE_QUESTION`, `UNKNOWN` | → deep reasoning |
| `deep_reasoning_model_profile` | Deep reasoning | All types | (terminal) |
| `fallback_model_profile` | Fallback | All types | (terminal) |

**Critical:** All `model_id`, `context_limit`, budget, and timeout values are placeholders.  They MUST be set from benchmark results or explicit configuration.  No values are assumed.

### Cache key

```
model_id + model_profile_version + prompt_schema_version + output_language + repository_fingerprint
```

## Relationship to Phase 3 (Grounded Analysis)

Phase 3 will use the `ExecutionBrief` from the intake gate as the input contract.  The brief provides:
- Scoped task definition (no ambiguity passed to the model)
- Explicit assumptions (model knows what was assumed)
- Evidence requirements (model knows what to look for)
- Stop conditions (model knows when to stop)
- Safe defaults (model operates within documented boundaries)

The intake gate ensures Phase 3 never receives an ill-defined request.

## Relationship to Phase 4 (Isolated Patch Validation)

Phase 4 will receive patch proposals that have been through the intake gate.  The intake gate ensures:
- Target files are explicitly identified
- Acceptance criteria are defined before patching
- Patches are only applied in temporary worktrees
- The original request is preserved in the execution brief

## Intake Contract

The complete `IntakeContract` captures every decision field:

```
request_id, original_request, normalized_request, detected_task_type,
decision, confidence, resolved_scope, safe_defaults, assumptions,
missing_information, clarifying_questions, risk_level,
evidence_requirements, expected_output_contract, blocking_reasons,
policy_version, created_at_utc
```

## Known Limitations

1. **Keyword-based classification:** The classifier uses regex pattern matching, not semantic understanding.  Ambiguous requests may be over- or under-classified.
2. **No repository context in classification:** The classifier does not inspect the repository to determine if a request makes sense.  This is deferred to Phase 3.
3. **Bilingual coverage is partial:** Spanish patterns cover common phrasing but not all dialects or informal expressions.
4. **Safe defaults are conservative:** Many request types have no safe defaults, requiring clarification.  This is intentional but may slow throughput.
5. **Risk assessment is rule-based:** Risk levels are determined by task type and evidence availability, not by inspecting the actual change content.

## Deferred Validation Status

All test fixtures are written but NOT executed while Test 2 benchmark is active.

Deferred validation commands:

```bash
# After Test 2 completes:
pytest agent_solution/tests/test_intake.py -v
ruff check agent_solution/intake/
ruff check agent_solution/tests/test_intake.py
```

No benchmarks, builds, lints, or model workloads were touched during implementation.
