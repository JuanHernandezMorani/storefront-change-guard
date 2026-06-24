import { describe, it, expect } from "vitest";
import { calculateShipping, FREE_SHIPPING_THRESHOLD_CENTS, STANDARD_SHIPPING_FEE_CENTS } from "./shipping";
import { toCents } from "./money";

describe("calculateShipping", () => {
  it("charges standard shipping when subtotal is below the threshold", () => {
    const subtotal = toCents(49.99);
    expect(calculateShipping(subtotal)).toBe(STANDARD_SHIPPING_FEE_CENTS);
  });

  it("grants free shipping when subtotal is exactly equal to the threshold", () => {
    const subtotal = FREE_SHIPPING_THRESHOLD_CENTS;
    expect(calculateShipping(subtotal)).toBe(0);
  });

  it("grants free shipping when subtotal is above the threshold", () => {
    const subtotal = toCents(75.5);
    expect(calculateShipping(subtotal)).toBe(0);
  });

  it("rejects fractional cent subtotals", () => {
    expect(() => calculateShipping(5000.5)).toThrow(
      "Subtotal must be an integer"
    );
  });

  it("rejects negative subtotal", () => {
    expect(() => calculateShipping(-1)).toThrow("Subtotal must not be negative");
  });

  it("rejects non-finite subtotal", () => {
    expect(() => calculateShipping(NaN)).toThrow("Subtotal must be a finite number");
    expect(() => calculateShipping(Infinity)).toThrow("Subtotal must be a finite number");
  });
});
