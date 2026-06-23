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
  if (!Number.isFinite(cents)) {
    throw new Error("Cents must be a finite number");
  }
  if (cents < 0) {
    throw new Error("Cents must not be negative");
  }
  return cents / 100;
}
