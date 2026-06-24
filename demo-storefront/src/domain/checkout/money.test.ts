import { describe, it, expect } from "vitest";
import { toCents, toDisplay, assertNonNegativeIntegerCents } from "./money";

describe("assertNonNegativeIntegerCents", () => {
  it("accepts zero", () => {
    expect(() => assertNonNegativeIntegerCents(0)).not.toThrow();
  });

  it("accepts positive integers", () => {
    expect(() => assertNonNegativeIntegerCents(5000)).not.toThrow();
  });

  it("rejects non-finite values", () => {
    expect(() => assertNonNegativeIntegerCents(NaN)).toThrow(
      "Cents must be a finite number"
    );
    expect(() => assertNonNegativeIntegerCents(Infinity)).toThrow(
      "Cents must be a finite number"
    );
  });

  it("rejects fractional values", () => {
    expect(() => assertNonNegativeIntegerCents(5000.5)).toThrow(
      "Cents must be an integer"
    );
    expect(() => assertNonNegativeIntegerCents(0.1)).toThrow(
      "Cents must be an integer"
    );
  });

  it("rejects negative values", () => {
    expect(() => assertNonNegativeIntegerCents(-1)).toThrow(
      "Cents must not be negative"
    );
  });

  it("uses custom label when provided", () => {
    expect(() => assertNonNegativeIntegerCents(5000.5, "Subtotal")).toThrow(
      "Subtotal must be an integer"
    );
  });
});

describe("toDisplay", () => {
  it("converts whole cents to dollars", () => {
    expect(toDisplay(5000)).toBe(50);
  });

  it("converts zero cents to zero dollars", () => {
    expect(toDisplay(0)).toBe(0);
  });

  it("converts standard shipping fee cents to dollars", () => {
    expect(toDisplay(599)).toBe(5.99);
  });

  it("rejects fractional cents", () => {
    expect(() => toDisplay(5000.5)).toThrow("Cents must be an integer");
  });

  it("rejects negative cents", () => {
    expect(() => toDisplay(-1)).toThrow("Cents must not be negative");
  });

  it("rejects non-finite cents", () => {
    expect(() => toDisplay(NaN)).toThrow("Cents must be a finite number");
  });
});

describe("toCents", () => {
  it("converts dollars to integer cents", () => {
    expect(toCents(50)).toBe(5000);
  });

  it("rounds fractional cents to nearest integer", () => {
    expect(toCents(49.99)).toBe(4999);
  });

  it("rejects negative amounts", () => {
    expect(() => toCents(-1)).toThrow("Amount must not be negative");
  });

  it("rejects non-finite amounts", () => {
    expect(() => toCents(NaN)).toThrow("Amount must be a finite number");
  });
});
