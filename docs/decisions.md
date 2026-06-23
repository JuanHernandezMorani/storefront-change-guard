# Decision Log

This document records material design choices as they are made. Entries should include the decision, rationale, alternatives considered, and follow-up validation.

| ID | Date | Decision | Status |
|---|---|---|---|
| D-001 | 2026-06-23 | Use a local-first, OpenAI-compatible model interface rather than requiring a hosted model provider. | Accepted |
| D-002 | 2026-06-23 | Prioritize operability, privacy, response time, then cost. | Accepted |
| D-003 | 2026-06-23 | Make code review and defect detection/fix validation the core scope; readiness decision is integrated into the same workflow. | Accepted |
| D-004 | 2026-06-23 | Keep the original candidate branch immutable; validate suggested patches only in temporary Git worktrees. | Accepted |
| D-005 | 2026-06-23 | Use deterministic checks and explicit policy gates as the decision authority; LLM output remains advisory and evidence-bound. | Accepted |

## Entry template

### D-XXX — Title

- **Date:** YYYY-MM-DD
- **Status:** Proposed / Accepted / Superseded / Rejected
- **Decision:**
- **Context:**
- **Alternatives considered:**
- **Consequences:**
- **Validation evidence:**
