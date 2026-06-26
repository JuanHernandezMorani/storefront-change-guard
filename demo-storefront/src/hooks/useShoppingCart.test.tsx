import { describe, it, expect } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { useShoppingCart } from "./useShoppingCart";

function OutsideProviderConsumer() {
  useShoppingCart();
  return null;
}

describe("useShoppingCart provider boundary", () => {
  it("throws when used outside ShoppingCartProvider", () => {
    expect(() => renderToStaticMarkup(<OutsideProviderConsumer />)).toThrow(
      "useShoppingCart must be used within a ShoppingCartProvider"
    );
  });
});
