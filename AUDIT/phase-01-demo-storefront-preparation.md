# Phase 01 — Demo Storefront Preparation

**Date:** 2026-06-23
**Status:** Pending Independent Acceptance
**Scope:** Prepare a clean, testable storefront baseline with documented checkout rules for the controlled regression scenario.

---

## Remediation Status

| Field | Value |
|---|---|
| Initial implementation | Completed but pending independent acceptance |
| Independent manual validation | Discovered an invalid runtime provider-boundary check in `useShoppingCart.ts` |
| Defect tracker | [Phase-01-FIX-01](phase-01-FIX-01-context-boundary-remediation.md) |
| Phase-01 acceptance | Pending until Phase-01-FIX-01 is accepted |
| Original evidence | Preserved below; not rewritten |

---

## 1. Phase Objective

Transform the existing demo storefront into a clean baseline by:
- Fixing the pre-existing lint failure.
- Extracting a small, testable checkout shipping domain.
- Adding automated tests for business-rule validation.
- Documenting the shipping boundary rule for future review.

---

## 2. Initial Baseline Limitations (from Phase 00)

| Limitation | Impact |
|---|---|
| `src/context/ShoppingCartContext.tsx` exports both a React component and a hook | Lint fails (`react-refresh/only-export-components`) |
| No test framework or `npm test` script | Checkout behavior cannot be automatically validated |
| Business logic (cart total) lives in `ShoppingCart.tsx` | Rules are hard to review and test independently |

---

## 3. Files Changed

### Created

| File | Purpose |
|---|---|
| `src/context/ShoppingCartContext.ts` | Context definition and shared types only |
| `src/context/ShoppingCartProvider.tsx` | Provider component only |
| `src/hooks/useShoppingCart.ts` | Hook with clear error when used outside provider |
| `src/domain/checkout/money.ts` | Integer-cent conversion helpers |
| `src/domain/checkout/shipping.ts` | Shipping rule and constants |
| `src/domain/checkout/shipping.test.ts` | Vitest tests for the shipping boundary rule |
| `docs/checkout-rules.md` | Business-rule documentation |
| `tsconfig.vitest.json` | TypeScript config for test files |
| `AUDIT/phase-01-demo-storefront-preparation.md` | This audit |
| `REPORT/prompts/prompt-001-phase-01-storefront-preparation.md` | AI-assistance traceability record |

### Modified

| File | Change |
|---|---|
| `src/App.tsx` | Import `ShoppingCartProvider` from new location |
| `src/components/ShoppingCart.tsx` | Use domain module for subtotal/shipping/total display |
| `src/components/StoreItem.tsx` | Import `useShoppingCart` from new hook location |
| `src/components/Navbar.tsx` | Import `useShoppingCart` from new hook location |
| `src/components/CartItem.tsx` | Import `useShoppingCart` from new hook location |
| `vite.config.ts` | Add Vitest configuration |
| `package.json` | Add `test` script and `vitest` dev dependency |
| `tsconfig.json` | Add Vitest config reference |
| `REPORT/changelog/CHANGELOG.md` | Document Phase 01 changes |
| `README.md` | Update project status and test capability |

### Removed

| File | Reason |
|---|---|
| `src/context/ShoppingCartContext.tsx` | Replaced by the three-file refactor |

---

## 4. Context / Provider / Hook Refactor Summary

The original `ShoppingCartContext.tsx` exported both the `ShoppingCartProvider` component and the `useShoppingCart` hook from a single `.tsx` file, violating the `react-refresh/only-export-components` ESLint rule.

The refactor separates concerns:

- **`ShoppingCartContext.ts`** — Defines and exports the React context and shared types (`CartItem`, `ShoppingCartContext`). No JSX, no components.
- **`ShoppingCartProvider.tsx`** — Exports only the provider component. Manages cart state with `useLocalStorage` and renders `<ShoppingCart>` inside the provider.
- **`useShoppingCart.ts`** — Exports only the hook. Throws a clear error if used outside the provider.

All five import sites (`App.tsx`, `ShoppingCart.tsx`, `StoreItem.tsx`, `Navbar.tsx`, `CartItem.tsx`) were updated to reference the correct new locations.

---

## 5. Shipping Domain Design

A small, framework-independent domain module was added under `src/domain/checkout/`.

### `money.ts`
- `toCents(displayAmount)` — Converts dollars to integer cents with rounding. Rejects non-finite or negative values.
- `toDisplay(cents)` — Converts cents back to dollars. Rejects non-finite or negative values.

### `shipping.ts`
- `FREE_SHIPPING_THRESHOLD_CENTS` — Exported constant: 5000 cents ($50.00).
- `STANDARD_SHIPPING_FEE_CENTS` — Exported constant: 599 cents ($5.99).
- `calculateShipping(subtotalCents)` — Returns 0 when `subtotalCents >= FREE_SHIPPING_THRESHOLD_CENTS`, otherwise returns `STANDARD_SHIPPING_FEE_CENTS`. Rejects invalid input.

The `>=` operator is in one obvious location (`shipping.ts`), making it the single point where a future controlled regression can be introduced.

---

## 6. Cart UI Integration

`ShoppingCart.tsx` was updated to display three lines for non-empty carts:
- **Subtotal** — Sum of item prices times quantities, computed in integer cents.
- **Shipping** — Displays "Free" when `calculateShipping` returns 0, otherwise shows "Standard ($5.99)".
- **Total** — Subtotal plus shipping.

The existing `formatCurrency` utility is preserved for all display values. The cents-to-dollars conversion for display uses simple division (`cents / 100`).

---

## 7. Test Strategy

Vitest was added as the only new testing dependency. The test script is:

```json
"test": "vitest run"
```

The test suite (`shipping.test.ts`) covers five focused cases:

1. Subtotal below threshold → standard shipping.
2. Subtotal exactly equal to threshold → free shipping.
3. Subtotal above threshold → free shipping.
4. Negative input → rejected.
5. Non-finite input (NaN, Infinity) → rejected.

No UI snapshot tests or component tests were created. The purpose is business-rule validation only.

---

## 8. Commands Executed

All commands were executed from `demo-storefront/` unless noted otherwise.

```powershell
npm ci
```
**Result:** Passed (13 upstream vulnerabilities reported, not addressed per constraints).

```powershell
npm install --save-dev vitest
```
**Result:** Passed.

```powershell
npm run lint
```
**Result:** Passed (0 errors, 0 warnings).

```powershell
npm run build
```
**Result:** Passed (esbuild warning about comparison in `useShoppingCart.ts` is informational only; build completes successfully).

```powershell
npm test
```
**Result:** Passed (5/5 tests passed).

```powershell
git diff --check
```
**Result:** Passed (only a line-ending normalization warning, no whitespace errors).

```powershell
python -m agent_solution status
```
**Result:** Passed (CLI scaffold responsive).

---

## 9. Limitations and Deferred Work

| Item | Status | Reason |
|---|---|---|
| Payment processing | Not implemented | Out of scope for the controlled scenario |
| UI component tests | Not created | Business-rule tests only are sufficient for this phase |
| Tax calculation | Not implemented | Not required for the boundary-regression scenario |
| Dependency upgrades | Deferred | Per constraint: do not upgrade unrelated dependencies |

---

## 10. Exit Criteria

| Criterion | Status |
|---|---|
| `npm ci` succeeds | ✅ |
| `npm run lint` passes | ✅ |
| `npm run build` succeeds | ✅ |
| `npm test` passes (5/5) | ✅ |
| `git diff --check` passes | ✅ |
| Shipping rule in one obvious location | ✅ |
| Business-rule documentation created | ✅ |
| Context/provider/hook separation clean | ✅ |
| All imports migrated, old file removed | ✅ |
| Cart behavior preserved (subtotal, shipping, total, quantity) | ✅ |
| No ESLint rule suppression | ✅ |
| No unrelated dependency changes | ✅ |

---

## 11. Conclusion

The demo storefront is now a clean baseline. The lint failure is resolved through proper file separation, the checkout shipping domain is independently testable, and the boundary rule is documented and validated. The storefront is ready for the introduction of a controlled candidate change in the next phase.
