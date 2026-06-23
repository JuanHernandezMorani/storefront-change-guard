# Phase 00 — Repository Baseline

**Date:** 2026-06-23
**Status:** Complete
**Scope:** Establish the technical baseline of the selected e-commerce storefront before introducing the controlled checkout regression scenario or implementing the review agent.

---

## 1. Repository Identification

| Field                     | Value                                       |
| ------------------------- | ------------------------------------------- |
| Local path                | `demo-storefront`                           |
| Package name              | `cart-system-typescript`                    |
| Repository type           | React + TypeScript shopping cart storefront |
| Package manager           | npm                                         |
| Lockfile                  | `package-lock.json`                         |
| Runtime used for baseline | Node.js `v24.15.0`                          |
| Package manager version   | npm `11.12.1`                               |

The upstream repository attribution and license information are preserved in `demo-storefront/UPSTREAM.md` and `demo-storefront/LICENSE`.

---

## 2. Detected Technology Stack

| Area                      | Technology                                   |
| ------------------------- | -------------------------------------------- |
| UI framework              | React `19.1.0`                               |
| Language                  | TypeScript `~5.8.3`                          |
| Build tool                | Vite `7.0.0`                                 |
| Styling and UI components | Bootstrap `5.3.7`, React Bootstrap `2.10.10` |
| Routing                   | React Router DOM `7.6.3`                     |
| Static analysis           | ESLint `9.29.0`                              |
| Existing test framework   | Not present                                  |

---

## 3. Baseline Validation

### 3.1 Dependency installation

```powershell
npm ci
```

**Result:** Passed.

Dependencies were installed from the committed `package-lock.json`.

`npm ci` reported 13 dependency vulnerabilities:

| Severity | Count |
| -------- | ----: |
| Low      |     2 |
| Moderate |     4 |
| High     |     7 |
| Total    |    13 |

This report is recorded as an upstream dependency observation. No automatic dependency upgrade was executed because it is outside the prototype's focused checkout-review scenario and could alter the reproducible baseline.

### 3.2 Static analysis

```powershell
npm run lint
```

**Result:** Failed.

```text
src/context/ShoppingCartContext.tsx
27:17 error react-refresh/only-export-components
```

**Observed cause:** `ShoppingCartContext.tsx` exports both the `ShoppingCartProvider` component and the `useShoppingCart` hook. The configured React Fast Refresh rule expects component files to export components only.

**Classification:** Pre-existing baseline quality issue.

**Planned handling:** This issue will be addressed in the storefront preparation phase before creating the controlled candidate change. The agent design will also distinguish pre-existing baseline failures from failures introduced by a reviewed change.

### 3.3 Production build

```powershell
npm run build
```

**Result:** Passed.

The TypeScript build and Vite production build completed successfully.

```text
vite v7.0.0 building for production...
✓ 367 modules transformed.
✓ built in 1.45s
```

### 3.4 Automated tests

```powershell
npm test
```

**Result:** Not available.

The repository does not include a test framework or a `test` script.

**Risk:** The existing project cannot validate checkout behavior or protect business-rule boundaries automatically.

**Planned handling:** A minimal Vitest suite will be added in the storefront preparation phase. Tests will focus only on the controlled checkout rule used in the prototype.

---

## 4. Relevant Source Structure

The project is compact and suitable for a focused controlled scenario.

| File                                  | Relevance                                                                                              |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `src/components/ShoppingCart.tsx`     | Calculates and displays the current cart total. Primary UI integration point for checkout information. |
| `src/context/ShoppingCartContext.tsx` | Stores cart items and provides cart operations. Contains the baseline lint failure.                    |
| `src/components/CartItem.tsx`         | Displays per-item price and quantity.                                                                  |
| `src/components/StoreItem.tsx`        | Displays product pricing and cart actions.                                                             |
| `src/utilities/formatCurrency.ts`     | Existing formatting helper for currency values.                                                        |
| `src/data/items.json`                 | Source product catalogue used by the cart.                                                             |

No dedicated checkout, shipping, tax, promotion, or order-domain module exists in the upstream structure.

---

## 5. Design Decision: Controlled Checkout Domain

The future scenario will not place new pricing rules directly inside `ShoppingCart.tsx`.

A small domain layer will be added during Phase 01, with responsibilities separated from the UI:

```text
src/
├── domain/
│   └── checkout/
│       └── shipping.ts
├── tests/
│   └── shipping.test.ts
└── components/
    └── ShoppingCart.tsx
```

This makes the business rule independently testable, easier to review, and appropriate for a code-review agent that needs to connect implementation details with documented behavior.

---

## 6. Baseline Risks

| Risk                                    | Impact                                               | Planned Mitigation                                                        |
| --------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------- |
| Existing lint failure                   | The repository is not initially quality-gate clean.  | Refactor the context/provider/hook boundary in Phase 01.                  |
| No test suite                           | Checkout behavior cannot be automatically validated. | Add minimal Vitest coverage focused on the demo rule.                     |
| Business logic located in UI components | Rules become harder to review and test.              | Extract controlled checkout logic into a small domain module.             |
| Dependency vulnerability summary        | May indicate upstream dependency maintenance debt.   | Record only; do not expand prototype scope with bulk dependency upgrades. |

---

## 7. Exit Criteria Status

| Criterion                                             | Status   |
| ----------------------------------------------------- | -------- |
| Storefront dependencies can be installed reproducibly | Complete |
| Existing build command identified and executed        | Complete |
| Existing lint command identified and executed         | Complete |
| Existing test capability assessed                     | Complete |
| Checkout-related implementation area identified       | Complete |
| Upstream attribution preserved                        | Complete |
| Controlled scenario location selected                 | Complete |

---

## 8. Phase 00 Conclusion

The selected storefront is an appropriate base for the prototype because it is small, understandable, and includes a real cart-total flow. It compiles successfully and has a deterministic npm-based installation process.

The baseline does contain one lint failure and no automated tests. These limitations will be corrected deliberately in the next phase before the controlled candidate change is introduced.

The next phase will prepare a clean, testable storefront baseline with documented checkout behavior. The review agent will then be implemented against a realistic candidate change that violates that documented behavior.

