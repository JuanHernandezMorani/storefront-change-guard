import { useContext } from "react";
import { ShoppingCartContext } from "../context/ShoppingCartContext";

export function useShoppingCart() {
  const context = useContext(ShoppingCartContext);
  if (context === ({} as import("../context/ShoppingCartContext").ShoppingCartContext)) {
    throw new Error(
      "useShoppingCart must be used within a ShoppingCartProvider"
    );
  }
  return context;
}
