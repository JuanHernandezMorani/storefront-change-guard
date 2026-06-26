# Phase-03-FIX-08 — Explicit File Scope Priority

## Trigger

The Phase 03 A-D live-gate runner invoked Gate A with the explicit request:

```text
Review shipping.py.
```

The result was `INSUFFICIENT_EVIDENCE` before any model call, even though
`shipping.py` exists and the same target had previously produced a valid 9B
structured response.

The returned limitation reported that all evidence records were excluded during
context reduction. The final reduced empty prompt fit the context window, but
the last non-empty bundle did not. The report therefore looked contradictory
because it displayed the empty-prompt total rather than the last non-empty
bundle total.

## Root cause

The evidence builder added broad staged/unstaged diff artifacts before the
explicit target file. The context reducer removed records from the end of the
list, so it removed `shipping.py` first and retained unrelated implementation
diff evidence until the final removal.

This violated the intended authority boundary: a named file is the requested
review scope, while a broad working-tree diff may be unrelated noise.

## Correction

1. For `CODE_REVIEW`, `BUG_DIAGNOSIS`, and `CODEBASE_QUESTION` requests with
   explicit file targets, collect the named eligible file(s) as the Phase 03
   evidence bundle and omit generic working-tree diff/excerpt evidence.
2. During any remaining context reduction, remove generic diff evidence before
   file excerpts, search results, and explicit targets.
3. Report the last non-empty budget when no non-empty bundle can fit.

## Scope and safety

- No model fallback, routing, retry, cloud dependency, or second model call.
- No parser relaxation.
- No mutation of the repository under review.
- Phase 03 still requires real Gates A-D after this correction.

## Acceptance criteria

- A broad unrelated local diff cannot prevent `Review shipping.py.` from
  collecting `shipping.py` evidence.
- The target file is retained as `EXPLICIT_PATH`.
- A model invocation remains possible when the explicit target fits the
  configured context budget.
- Deterministic tests, Ruff, compileall, and Git whitespace checks pass.
