import { createContext } from "react";

export type CartItem = {
  id: number;
  quantity: number;
};

export type ShoppingCartContext = {
  cartQuantity: number;
  cartItems: CartItem[];
  openCart: () => void;
  closeCart: () => void;
  getItemQuantity: (id: number) => number;
  increaseCartQuantity: (id: number) => void;
  decreaseCartQuantity: (id: number) => void;
  removeFromCart: (id: number) => void;
};

export const ShoppingCartContext = createContext({} as ShoppingCartContext);
