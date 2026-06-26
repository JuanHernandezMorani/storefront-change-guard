/**
 * Assert that a value is a finite, non-negative integer representing cents.
 * Rejects fractional cents (e.g. 5000.5) because a cent cannot be divided.
 */
export function assertNonNegativeIntegerCents(
  cents: number,
  label = "Cents"
): void {
  if (!Number.isFinite(cents)) {
    throw new Error(`${label} must be a finite number`);
  }
  if (!Number.isInteger(cents)) {
    throw new Error(`${label} must be an integer`);
  }
  if (cents < 0) {
    throw new Error(`${label} must not be negative`);
  }
}

/**
 * Safe conversion from a display amount (dollars) to integer cents.
 * Rounds to the nearest cent to avoid floating-point drift.
 */
export function toCents(displayAmount: number): number {
  if (!Number.isFinite(displayAmount)) {
    throw new Error("Amount must be a finite number");
  }
  if (displayAmount < 0) {
    throw new Error("Amount must not be negative");
  }
  return Math.round(displayAmount * 100);
}

/**
 * Convert integer cents back to a display amount in dollars.
 */
export function toDisplay(cents: number): number {
  assertNonNegativeIntegerCents(cents);
  return cents / 100;
}
