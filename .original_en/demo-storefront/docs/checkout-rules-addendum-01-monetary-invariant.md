# Checkout Rules Addendum 01 — Monetary Invariant

**Date:** 2026-06-23
**Related work:** `Phase-01-FIX-02`
**Reference:** [`checkout-rules.md`](checkout-rules.md)

---

## Purpose

This document is an addendum to the original [checkout-rules.md](checkout-rules.md). It clarifies the monetary invariant enforced by the integer-cent domain model without altering the original checkout rules, which remain immutable historical evidence.

---

## Monetary Invariant

Business-domain monetary values represented as cents must satisfy all of the following constraints:

1. **Finite** — The value must be a finite number. `NaN` and `Infinity` are rejected.
2. **Non-negative** — The value must be zero or greater. Negative cent values are rejected.
3. **Integer** — The value must be a whole number. Fractional-cent values are rejected.

### Fractional-Cent Rejection

Values such as `5000.5` cents are **invalid** in this domain model. A cent cannot be subdivided; therefore, fractional-cent inputs must be rejected at every public entry point that accepts integer-cent arguments.

The `assertNonNegativeIntegerCents()` helper enforces this invariant and throws a descriptive error when any constraint is violated.

---

## Display-to-Domain Conversion

Display amounts (dollars with two decimal places) may be converted to integer cents using the `toCents()` function. This function:

- Accepts a finite, non-negative display amount.
- Rounds to the nearest whole cent using standard rounding rules.
- Returns an integer-cent value suitable for business-domain calculations.

Example:

```text
toCents(50.00) → 5000
toCents(50.005) → 5001  (rounded to nearest cent)
```

The rounding behavior is documented and must not be altered without a corresponding update to this addendum.

---

## Domain Calculation Input Contract

All business-domain calculations, including `calculateShipping()`, must receive **validated integer cents** as input. Callers must ensure that:

- Values originate from `toCents()` output, or
- Values have been validated by `assertNonNegativeIntegerCents()` before use.

Passing unvalidated or fractional-cent values into domain functions violates the domain contract and will result in a thrown error.

---

## Compatibility with Free-Shipping Boundary Rule

This addendum does **not** alter the free-shipping boundary rule documented in [checkout-rules.md](checkout-rules.md). The boundary operator (`>=`), the free-shipping threshold ($50.00 / 5000 cents), and the standard shipping fee ($5.99 / 599 cents) remain unchanged.

The monetary invariant described here applies to all integer-cent values used in the checkout domain, including the free-shipping threshold and subtotal inputs to `calculateShipping()`.

---

## Historical Evidence

The original [checkout-rules.md](checkout-rules.md) remains immutable. This addendum exists to clarify the monetary invariant introduced and enforced during `Phase-01-FIX-02` without rewriting historical documentation.
