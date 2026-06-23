import { Col, Row } from "react-bootstrap";
import storeItems from "../data/items.json";
import { StoreItem } from "../components/StoreItem";

export function Home() {
  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="mb-0 fw-bold">Add Items to Cart</h1>
      </div>
      <Row md={2} xs={1} lg={3} className="g-3 text-white">
        {storeItems.map(item => (
            <Col key={item.id}>< StoreItem {...item}/></Col>
        ))}
      </Row>{" "}
    </>
  );
}
