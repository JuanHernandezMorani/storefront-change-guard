# Checkout Shipping Rules

## Purpose

This document describes the controlled checkout domain added to the demo storefront for the technical challenge prototype. It defines the shipping boundary rule used to evaluate whether a code review system can detect, explain, and correct a regression.

## Currency Convention

All monetary values in the storefront are represented as **USD dollars** in the user interface. Internal business-rule calculations use **integer cents** to avoid floating-point precision issues.

Example: `$50.00` is stored as `5000` cents internally.

## Free-Shipping Threshold

The free-shipping threshold is **$50.00** (5000 cents).

## Standard Shipping Fee

The standard shipping fee is **$5.99** (599 cents).

## Shipping Rule

Free shipping applies when the cart subtotal is **equal to or greater than** the free-shipping threshold.

| Subtotal | Threshold | Comparison     | Shipping Cost |
| -------- | --------- | -------------- | ------------- |
| $49.99   | $50.00    | below          | $5.99         |
| $50.00   | $50.00    | equal to       | Free          |
| $75.50   | $50.00    | above          | Free          |

The boundary operator is `>=` (greater than or equal to).

## Controlled Scenario

This is a controlled scenario added for the technical challenge prototype. It does **not** imply that the original upstream repository contained any defects. The shipping rule is intentionally designed so that a future controlled candidate change can introduce a boundary-condition regression by replacing `>=` with `>`.
