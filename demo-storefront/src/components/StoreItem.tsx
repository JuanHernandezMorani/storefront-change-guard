import { Button, Card } from "react-bootstrap";
import { formatCurrency } from "../utilities/formatCurrency";
import { useShoppingCart } from "../context/ShoppingCartContext";

type StoreItemProps = {
  id: number;
  name: string;
  description: string;
  price: number;
  imageUrl: string;
};

export function StoreItem({
  id,
  name,
  description,
  price,
  imageUrl,
}: StoreItemProps) {
  const {
    getItemQuantity,
    increaseCartQuantity,
    decreaseCartQuantity,
    removeFromCart,
  } = useShoppingCart();
  const quantity = getItemQuantity(id);
  return (
    <Card className="h-100 shadow-sm border-0">
      <Card.Img
        variant="top"
        src={imageUrl}
        height="200px"
        style={{ objectFit: "cover", width: "100%" }}
      />
      <Card.Body className="d-flex flex-column">
        <Card.Title className="d-flex justify-content-between align-items-baseline mb-3">
          <span className="fs-5">{name}</span>
          <span
            className="ms-2 text-primary"
            style={{
              fontWeight: "bold",
              fontSize: "1.1rem",
            }}
          >
            {formatCurrency(price)}
          </span>
        </Card.Title>
        <Card.Subtitle
          className="mb-3 text-secondary"
          style={{ fontSize: "0.8rem", fontStyle: "italic" }}
        >
          <span>{description}</span>
        </Card.Subtitle>
        <div className="mt-auto">
          {quantity === 0 ? (
            <Button
              className="w-100 shadow"
              variant="success"
              style={{
                fontWeight: "bold",
                letterSpacing: "1px",
                fontSize: "0.8rem",
              }}
              onClick={() => increaseCartQuantity(id)}
            >
              + Add to Cart
            </Button>
          ) : (
            <div
              className="d-flex align-items-center flex-column"
              style={{ gap: "0.5rem" }}
            >
              <div
                className="d-flex align-items-center jsutify-content-center"
                style={{ gap: "0.5rem" }}
              >
                <Button
                  className="shadow"
                  variant="danger"
                  style={{
                    fontWeight: "bold",
                    fontSize: "1rem",
                  }}
                  onClick={() => decreaseCartQuantity(id)}
                >
                  -
                </Button>
                <div>
                  <span
                    className="fs-3"
                    style={{
                      fontWeight: "normal",
                      fontSize: "0.5rem",
                    }}
                  >
                    {quantity}
                  </span>{" "}
                  in Cart
                </div>
                <Button
                  className="shadow"
                  variant="success"
                  style={{
                    fontWeight: "bold",
                    fontSize: "1rem",
                  }}
                  onClick={() => increaseCartQuantity(id)}
                >
                  +
                </Button>
              </div>
              <Button
                className="w-100 shadow"
                variant="danger"
                style={{
                  fontWeight: "bold",
                  letterSpacing: "1px",
                  fontSize: "0.8rem",
                }}
                onClick={() => removeFromCart(id)}
              >
                - Remove From Cart
              </Button>
            </div>
          )}
        </div>
      </Card.Body>
    </Card>
  );
}
