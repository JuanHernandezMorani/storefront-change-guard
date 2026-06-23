import { Container, Row, Col, Card } from "react-bootstrap";
import { FaCheckCircle, FaCode, FaReact, FaGithub } from "react-icons/fa";

export function About() {
  return (
    <Container>
      <Row className="mb-4">
        <Col>
          <h1 className="fw-bold mb-3">About This Project</h1>
          <p className="text-muted fs-4">
            A modern, minimal, and responsive shopping cart built with 
            <FaReact className="text-primary mx-1" /> React, TypeScript, and Bootstrap.
          </p>
        </Col>
      </Row>

      <Row className="mb-5">
        <Col md={6}>
          <Card className="shadow-sm border-0 mb-3">
            <Card.Body>
              <Card.Title className="fw-semibold mb-3">
                <FaCheckCircle className="text-success me-2" />
                Key Features
              </Card.Title>
              <ul className="list-unstyled ms-2">
                <li className="mb-2">🛒 Add and remove items from cart</li>
                <li className="mb-2">💾 Auto-saves cart using localStorage</li>
                <li className="mb-2">📱 Fully responsive layout</li>
                <li className="mb-2">✅ Written in strongly typed TypeScript</li>
              </ul>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card className="shadow-sm border-0">
            <Card.Body>
              <Card.Title className="fw-semibold mb-3">
                <FaCode className="text-info me-2" />
                About the Developer
              </Card.Title>
              <p>
                Hi, I’m <strong>PAIshanMadusha</strong> a passionate software
                engineering student focused on building clean and functional web apps.
                This project was created to improve my full-stack skills while
                showcasing modern frontend architecture.
              </p>
              <p className="mb-0 fw-bold">
                <a
                  href="https://github.com/PAIshanMadusha"
                  target="_blank"
                  rel="noreferrer"
                  className="text-decoration-none"
                >
                  <FaGithub className="me-2" />
                  View my GitHub Profile
                </a>
              </p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="text-center">
        <Col>
          <small className="text-muted">
            &copy; {new Date().getFullYear()} Cart System. Built with ❤️ by Ishan.
          </small>
        </Col>
      </Row>
    </Container>
  );
}
