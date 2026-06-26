# Presentation Outline

## Target duration

30 minutes, including a focused live demonstration and technical discussion.

## Suggested flow

1. **Problem and scope — 3 minutes**
   - E-commerce code changes need review, correction validation, and a clear
     decision boundary.
   - The prototype commits to evidence-grounded review and isolated validation;
     readiness policy is a third bounded capability.

2. **Architecture and authority boundaries — 4 minutes**
   - Show the request-to-readiness flow.
   - Distinguish advisory model analysis from deterministic evidence, patch,
     command, and policy controls.

3. **Model selection evidence — 4 minutes**
   - Explain why speed and memory measurements were necessary but insufficient.
   - Show the controlled 4B versus 9B structured-output result.
   - State the final single-model decision and no-fallback rule.

4. **Phase 03 live gates — 7 minutes**
   - Run or show the concise Gate A–D transcript.
   - Highlight evidence grounding, cache reuse, Spanish file-scoped Q&A, and
     safe insufficient-evidence behavior.

5. **Phase 04 isolated validation — 6 minutes**
   - Show the supplied patch scope and safety checks.
   - Show detached worktree execution, fixed validation commands, and unchanged
     source checkout.

6. **Phase 05 readiness — 3 minutes**
   - Show the two input artifacts and the `READY` result.
   - Explain that this policy has no model invocation or mutation authority.

7. **Trade-offs and limitations — 2 minutes**
   - Local model: privacy and cost benefits, with local setup and latency.
   - Bounded scope: safer and more auditable than broad autonomous behavior.
   - `READY` does not merge, deploy, or replace human review.

8. **Questions — 1 minute plus remaining time**

## Live-demo command order

1. `scripts/run_all_phase_validation.ps1 -Phase all`
2. `scripts/run_phase03_live_gates.ps1`
3. `scripts/run_phase04_live_validation.ps1`
4. `scripts/run_phase05_live_decision.ps1`

Use a prepared clean repository state. Keep the successful artifacts available
as evidence, not as a replacement for the demonstration.
