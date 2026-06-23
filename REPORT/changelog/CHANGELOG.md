# Changelog

All notable changes to this prototype will be documented in this file.

The format is based on Keep a Changelog and uses semantic categories where practical.

## [Unreleased]

### Added

- Initial project scaffolding.
- Documentation, audit, report, policy, and Python package foundations.
- Shopping-cart context refactor: separated `ShoppingCartContext.ts`, `ShoppingCartProvider.tsx`, and `useShoppingCart.ts` to resolve the React Fast Refresh lint failure.
- Checkout shipping domain (`src/domain/checkout/`): `money.ts` for integer-cent conversions, `shipping.ts` for the free-shipping boundary rule.
- Automated shipping boundary tests using Vitest (`shipping.test.ts`).
- Business-rule documentation for checkout shipping rules (`docs/checkout-rules.md`).
- **Phase-01-FIX-01:** Focused provider-boundary test (`useShoppingCart.test.tsx`) verifying `useShoppingCart()` throws outside `ShoppingCartProvider`.
- **Phase-01-FIX-01:** Remediation audit, prompt traceability, validation evidence, and change-register entry.

### Changed

- Updated cart UI to display subtotal, shipping, and total using the domain module.
- Added `vitest` as a dev dependency and `npm test` script.
- **Phase-01-FIX-01:** Replaced unsafe empty-object sentinel in `ShoppingCartContext` default with explicit `null`.
- **Phase-01-FIX-01:** Replaced invalid object-identity comparison in `useShoppingCart()` with reliable `null` guard.

### Fixed

- Resolved `react-refresh/only-export-components` lint failure by separating context, provider, and hook into individual files.
- **Phase-01-FIX-01:** Corrected invalid provider-boundary detection in `useShoppingCart()` hook that always evaluated to false, removing the associated Vite/esbuild build warning.

### Security

- Local-first configuration contract and default restrictions documented.
