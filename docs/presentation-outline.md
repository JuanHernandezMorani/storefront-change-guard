# Presentation Outline — Working Draft

## Target duration

30 minutes, including a live demonstration and technical discussion.

## Suggested flow

1. **Problem and scope (3 min)**
   - E-commerce development lifecycle friction.
   - Why the prototype focuses on code review, defect validation, and readiness decisions.

2. **Design priorities (3 min)**
   - Operability > Privacy > Response time > Cost.
   - Why local-first and deterministic validation matter.

3. **Architecture (5 min)**
   - Diff/context collection.
   - Deterministic checks.
   - Bounded model reasoning.
   - Evidence validation.
   - Isolated worktree validation.
   - Policy gate.

4. **Live Scenario A: buggy candidate change (10 min)**
   - Show documented business rule.
   - Run review command.
   - Inspect actionable finding and evidence.
   - Show suggested patch and isolated validation.
   - Show original branch decision.

5. **Live Scenario B: corrected candidate change (4 min)**
   - Run review against a ready candidate.
   - Show policy result and artifact difference.

6. **Trade-offs, limitations, and next steps (3 min)**
   - What was deliberately excluded.
   - How to scale safely with more time.

7. **Questions (2 min or remaining time)**

## Demo reliability checklist

- Use a clean cloned or reset state.
- Verify local model server before the presentation.
- Have pre-generated artifacts available only as a contingency, not as a substitute for the live run.
- Keep commands short and deterministic.
- Avoid relying on external internet access.
