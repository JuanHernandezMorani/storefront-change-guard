import { Offcanvas, Stack, Button } from "react-bootstrap";
import { useShoppingCart } from "../context/ShoppingCartContext";
import { CartItem } from "./CartItem";
import storeItems from "../data/items.json";
import { formatCurrency } from "../utilities/formatCurrency";

type ShoppingCartProps = {
  isOpen: boolean;
};

export function ShoppingCart({ isOpen }: ShoppingCartProps) {
  const { closeCart, cartItems } = useShoppingCart();

  const total = cartItems.reduce((total, cartItem) => {
    const item = storeItems.find((i) => i.id === cartItem.id);
    return total + (item?.price || 0) * cartItem.quantity;
  }, 0);

  return (
    <Offcanvas show={isOpen} onHide={closeCart} placement="end">
      <Offcanvas.Header closeButton className="bg-white text-black">
        <Offcanvas.Title
          style={{
            fontWeight: "bold",
            fontSize: "1.5rem",
            letterSpacing: "0.5px",
          }}
        >
          🛒 Your Cart
        </Offcanvas.Title>
      </Offcanvas.Header>

      <Offcanvas.Body className="d-flex flex-column justify-content-between">
        {cartItems.length > 0 ? (
          <>
            {/* Cart Items */}
            <Stack gap={3} className="mb-4">
              {cartItems.map((item) => (
                <CartItem key={item.id} {...item} />
              ))}
            </Stack>

            {/* Total + Checkout */}
            <div className="border-top pt-3 mt-2">
              <div className="d-flex justify-content-between align-items-center fw-bold fs-5">
                <span>Total:</span>
                <span className="text-success">{formatCurrency(total)}</span>
              </div>
              <Button
                variant="success"
                className="mt-3 w-100 fw-semibold"
                size="lg"
              >
                Proceed to Checkout
              </Button>
            </div>
          </>
        ) : (
          // Empty Cart Message
          <div className="text-center">
            <p className="text-muted fs-5">🛍️ Your Cart Is Empty!</p>
            <Button onClick={closeCart} variant="success">
              Continue Shopping
            </Button>
          </div>
        )}
      </Offcanvas.Body>
    </Offcanvas>
  );
}
