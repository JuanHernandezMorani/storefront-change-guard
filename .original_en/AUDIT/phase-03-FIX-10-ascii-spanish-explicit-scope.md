# Phase-03-FIX-10 — ASCII Spanish Explicit-File Scope

## Trigger

Phase 03 Gate C uses the Windows-safe Spanish request:

```text
Que hace calculate_shipping en shipping.py?
```

After Gate A and Gate B passed, Gate C returned `INSUFFICIENT_EVIDENCE` before
model execution.

## Root cause

The task classifier recognizes both `qué` and `que`, so the request correctly
classifies as `CODEBASE_QUESTION`. However, explicit target extraction was
stricter: it only recognized a file path placed immediately after directive
phrases such as `qué hace`. It therefore did not extract `shipping.py` from the
natural question form `Que hace calculate_shipping en shipping.py?`.

In addition, `CODEBASE_QUESTION` scope resolution always selected generic
bounded repository search, even when an explicit target had been extracted.
This discarded the target authority boundary and allowed unrelated in-progress
working-tree changes to consume the evidence budget.

## Correction

1. Extract safe repository-relative Python path tokens wherever they occur in a
   request, rather than only after a fixed directive phrase.
2. Reject absolute paths and path-traversal forms from explicit extraction.
3. Preserve explicit targets through `CODEBASE_QUESTION` safe defaults and
   resolved scope.
4. Reuse the existing Phase 03 explicit-target evidence policy: an explicit
   file question uses the named file as the bounded evidence authority.

## Acceptance criteria

- `Que hace calculate_shipping en shipping.py?` is classified as
  `CODEBASE_QUESTION`.
- Its resolved scope contains exactly `shipping.py`.
- With a large unrelated working-tree diff, its evidence bundle contains only
  the named file and can proceed to the model.
- Absolute and traversal paths are not extracted as repository targets.

## Non-goals

- No model, parser, completion limit, cache policy, retry behavior, or cloud
  dependency is changed.
- No repository mutation is performed by the analysis runtime.
