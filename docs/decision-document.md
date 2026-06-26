# Storefront Change Guard — Decision Document

## Problem and selected scope

Storefront Change Guard is a local-first prototype for e-commerce development
workflows. The selected scope demonstrates three linked capabilities:

1. evidence-grounded code review;
2. correction validation in an isolated worktree; and
3. deterministic readiness decisions.

The challenge minimum is at least two capabilities. The primary demonstrable
pair is review plus defect/correction validation; the policy layer provides a
third bounded capability.

## Architecture

The workflow separates advisory language-model reasoning from deterministic
control:

```text
intake + Git evidence
→ single local model analysis
→ evidence and schema validation
→ supplied patch in detached worktree
→ fixed validation commands
→ deterministic readiness policy
```

The original checkout is never automatically changed, committed, merged, or
pushed. A model has no shell authority and cannot claim a test passed.

## Trade-offs

### Cost

The default product path uses one local model and no hosted inference provider.
The trade-off is local setup and hardware requirements. Model weights are not
included in delivery because they are large runtime assets, not source code.

### Latency

Local inference can be slower than a hosted API, so Phase 03 bounds evidence,
context, model calls, and expansion. Phase 04 and Phase 05 contain no model
calls.

### Privacy

Repository evidence remains local. Raw prompts, raw model output, and private
reasoning are not stored in cache/session artifacts. The model runner exposes
only sanitized model content to the strict envelope parser.

### Operability

The repository includes a phase-scoped test runner, explicit artifacts,
allowlisted validation commands, and a delivery runbook. The trade-off is that
safety constraints reject broad autonomous behavior instead of guessing.

## Alternatives considered

- **Cloud-only agent:** faster setup but weaker privacy and recurring cost.
- **Unrestricted agent shell access:** more automation but unacceptable source
  mutation and command-injection risk.
- **Vector database / multi-agent routing:** not required for the challenge and
  adds operational surface without improving the controlled demo.
- **Automatic merge after patch validation:** deliberately excluded; readiness
  is not merge authority.

## Evidence and evaluation

Phase 02 supplies bounded Git context. Phase 03 validates structured claims
against evidence IDs. Phase 04 records patch safety, worktree execution and
command status. Phase 05 applies fixed rules to those prior artifacts. The
final demonstration shows both a positive controlled correction path and a
negative safety path.

## AI assistance disclosure

AI tools were used as engineering assistants for analysis, drafting,
implementation support, test design and review. The author retained design
ownership, scope control, evidence standards, validation criteria, final
runtime execution, debugging and delivery approval.
