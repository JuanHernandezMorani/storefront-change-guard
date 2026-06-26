# Phase, Fix, and Enhancement Traceability Policy

## Purpose

This project treats implementation phases, corrective work, and visual or usability improvements as separate, traceable engineering artifacts.

The objective is not only to deliver a functioning prototype. The objective is to preserve evidence of how the system was designed, validated, corrected, and improved.

Every record must make clear:

* What was implemented or changed.
* Why the work was necessary.
* Which phase owns the work.
* What caused the issue or improvement request.
* Which alternatives were considered.
* Why the selected solution was chosen.
* How the result was independently validated.

This policy supports quality over breadth and prevents completed work from being silently rewritten after later findings.

---

## Identifier Convention

The project uses three artifact types.

```text
Phase-NN
Phase-NN-FIX-NN
Phase-NN-ENHANCE-NN
```

Examples:

```text
Phase-01
Phase-01-FIX-01
Phase-01-FIX-02
Phase-01-ENHANCE-01
Phase-05-FIX-02
Phase-05-ENHANCE-03
```

### Identifier Meaning

| Identifier            | Meaning                                                                                                                                                                  |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Phase-NN`            | A planned implementation phase that introduces a new capability, integration, or validated scope of work.                                                                |
| `Phase-NN-FIX-NN`     | A corrective action required because a defect, failed validation, missing requirement, incorrect behavior, or blocking quality issue exists in work owned by `Phase-NN`. |
| `Phase-NN-ENHANCE-NN` | A non-blocking visual, aesthetic, UX, presentation, or usability improvement related to work owned by `Phase-NN`.                                                        |

The numbering restarts for each phase.

---

## Strict Phase Ownership

A fix or enhancement always belongs to the phase where the relevant implementation, defect, or improvement opportunity originated.

```text
Correct:
Phase-02-FIX-01 fixes a defect introduced by Phase-02.
Phase-05-ENHANCE-01 improves a UI or workflow introduced in Phase-05.
```

```text
Incorrect:
Phase-05-FIX-02 fixes a defect introduced by Phase-02.
Phase-04-ENHANCE-01 modifies unrelated work introduced in Phase-01.
```

If a later phase discovers an earlier defect, the report must preserve both facts:

```text
Originating phase: Phase-02
Detected during: Phase-05
Remediation identifier: Phase-02-FIX-01
```

The discovery phase does not change the ownership of the defect.

---

## When to Use a FIX

Create a `Phase-NN-FIX-NN` record when a defect requires correction before the owning phase can be accepted or remain accepted.

A fix is required when any of the following applies:

* A required validation command fails.
* A test, build, lint, runtime, security, or integration check exposes incorrect behavior.
* A documented business rule is violated.
* An implementation does not meet its stated acceptance criteria.
* A model-assisted implementation contains a real defect discovered during independent validation.
* A prior implementation contains misleading, unsafe, incomplete, or non-reproducible behavior.
* A visual issue prevents intended usage, accessibility, or acceptance criteria from being met.

A fix must not be classified as an enhancement merely because the correction is small.

---

## When to Use an ENHANCE

Create a `Phase-NN-ENHANCE-NN` record for a non-blocking improvement that does not repair a requirement failure.

Examples include:

* Improving spacing, hierarchy, typography, labels, or visual clarity.
* Improving a demo screen so results are easier to understand.
* Refining terminal output formatting.
* Improving report readability.
* Adding a non-essential UX affordance.
* Making an already-correct workflow easier to use or present.

An enhancement must not alter business behavior, readiness decisions, security boundaries, or validation logic unless that change is explicitly reviewed as a new phase or corrective fix.

---

## Required Artifacts

Every implementation phase, fix, and enhancement must have dedicated documentation.

| Artifact type         | Audit record                                 | Prompt traceability                                              | Validation evidence                                           |
| --------------------- | -------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------- |
| `Phase-NN`            | `AUDIT/phase-NN-<description>.md`            | `REPORT/prompts/prompt-NNN-phase-NN-<description>.md`            | `REPORT/executions/run-NNN-phase-NN-validation.md`            |
| `Phase-NN-FIX-NN`     | `AUDIT/phase-NN-FIX-NN-<description>.md`     | `REPORT/prompts/prompt-NNN-phase-NN-FIX-NN-<description>.md`     | `REPORT/executions/run-NNN-phase-NN-FIX-NN-validation.md`     |
| `Phase-NN-ENHANCE-NN` | `AUDIT/phase-NN-ENHANCE-NN-<description>.md` | `REPORT/prompts/prompt-NNN-phase-NN-ENHANCE-NN-<description>.md` | `REPORT/executions/run-NNN-phase-NN-ENHANCE-NN-validation.md` |

All completed work must also update:

```text
AUDIT/fix-register.md
REPORT/changelog/CHANGELOG.md
```

The original phase report must never be overwritten to hide a later defect. It may be updated only with a remediation-status reference.

---

## Required Content for FIX and ENHANCE Records

Every fix and enhancement report must include the following sections.

### 1. Identification

* Identifier.
* Parent phase.
* Date.
* Status.
* Author or owner.
* Related branch and commit, when available.

### 2. Reason for Existence

Clearly state why the record exists.

For fixes:

* Which requirement, validation, behavior, or quality rule failed.
* Why the issue blocks acceptance or requires correction.

For enhancements:

* Which visual, usability, or presentation limitation was identified.
* Why the improvement is useful even though existing behavior was correct.

### 3. Scope Ownership

* Originating phase.
* Detection phase, if different.
* Affected files.
* Affected behavior or presentation area.
* Explicit confirmation that the work does not modify unrelated phases.

### 4. Evidence

Include the exact evidence that motivated the work:

* Validation output.
* Test result.
* Build warning.
* Runtime behavior.
* Screenshot reference when relevant.
* Code location.
* Requirement reference.
* Review finding.

### 5. Root Cause Analysis

Explain the technical cause, not only the visible symptom.

The analysis must distinguish between:

* Triggering condition.
* Immediate technical cause.
* Contributing factors.
* Impact.
* Why prior validation did not catch the issue earlier.

### 6. Origin Classification

Use the following fields:

| Field               | Allowed values                                                                                                         |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `origin`            | `ai_generated`, `ai_assisted`, `human_authored`, `upstream_baseline`, `environment`, `unknown`                         |
| `model_involvement` | `direct`, `assisted`, `none`                                                                                           |
| `detection_source`  | `manual_validation`, `unit_test`, `lint`, `build`, `runtime_check`, `code_review`, `integration_test`, `visual_review` |
| `severity`          | `critical`, `high`, `medium`, `low`                                                                                    |
| `status`            | `open`, `in_progress`, `accepted`, `rejected`, `deferred`                                                              |

AI involvement must be attributed accurately. The record must describe the real technical failure rather than assigning generic blame to a model.

### 7. Alternatives Considered

Every fix or enhancement must evaluate alternatives when more than one reasonable solution exists.

Use a table such as:

| Option   | Description | Benefits | Risks or drawbacks | Decision |
| -------- | ----------- | -------- | ------------------ | -------- |
| Option A | ...         | ...      | ...                | Rejected |
| Option B | ...         | ...      | ...                | Selected |

The selected option must include a concise rationale tied to project priorities:

```text
Operability > Privacy > Response Time > Cost
```

### 8. Implemented Solution

Document:

* Files created, modified, or removed.
* Behavioral changes.
* Non-goals.
* Compatibility considerations.
* Why the implementation is limited to the owning phase.

### 9. Validation

List the exact commands or procedures executed after the change.

For every validation, record:

* Command or method.
* Working directory.
* Actual result.
* Evidence location when applicable.

No report may claim a passing result that was not actually observed.

### 10. Acceptance Criteria

Use a clear table:

| Criterion                        | Result      |
| -------------------------------- | ----------- |
| Root cause addressed             | Pass / Fail |
| Required behavior verified       | Pass / Fail |
| Required tests pass              | Pass / Fail |
| Build and lint pass              | Pass / Fail |
| No unrelated regression detected | Pass / Fail |
| Documentation updated            | Pass / Fail |

### 11. Final Disposition

The record must end with one of:

```text
Accepted
Rejected
Deferred
Still Open
```

---

## Phase Acceptance Rule

A phase is accepted only when:

1. Its declared scope is complete.
2. Its required validation commands pass.
3. Its documentation is complete and accurate.
4. No blocking `FIX` associated with that phase remains open.
5. Any enhancement required by the phase acceptance criteria is complete.
6. Any optional enhancement may remain open only when it does not affect correctness, operability, privacy, safety, accessibility, or required presentation behavior.

A phase with an open blocking fix must never be represented as accepted.

---

## Quality Principle

The project prioritizes quality, traceability, and reproducibility over the number of features delivered.

A smaller number of capabilities that are implemented, validated, documented, and defensibly explained is preferable to a broader but incomplete prototype.
