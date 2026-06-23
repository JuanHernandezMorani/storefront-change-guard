import { toCents } from "./money";

/**
 * Free shipping threshold in integer cents.
 * The original value is $50.00.
 */
export const FREE_SHIPPING_THRESHOLD_CENTS = toCents(50);

/**
 * Standard shipping fee in integer cents.
 * The original value is $5.99.
 */
export const STANDARD_SHIPPING_FEE_CENTS = toCents(5.99);

/**
 * Determine the shipping cost for a given subtotal in integer cents.
 * Free shipping applies when the subtotal is equal to or greater than
 * the threshold.
 */
export function calculateShipping(subtotalCents: number): number {
  if (!Number.isFinite(subtotalCents)) {
    throw new Error("Subtotal must be a finite number");
  }
  if (subtotalCents < 0) {
    throw new Error("Subtotal must not be negative");
  }
  return subtotalCents >= FREE_SHIPPING_THRESHOLD_CENTS
    ? 0
    : STANDARD_SHIPPING_FEE_CENTS;
}
