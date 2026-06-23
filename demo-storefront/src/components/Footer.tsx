import { Container, Row, Col } from "react-bootstrap";
import { FaGithub, FaLinkedin } from "react-icons/fa";

const Footer = () => {
  return (
    <footer className="bg-black text-light py-1 mt-auto">
      <Container>
        <Row className="justify-content-center">
          <Col
            md={4}
            className="d-flex justify-content-center align-items-center"
          >
            <div className="d-flex align-items-center gap-3">
              <a
                href="https://github.com/PAIshanMadusha"
                className="text-light fs-4"
                target="_blank"
                rel="noopener noreferrer"
              >
                <FaGithub />
              </a>
              <a
                href="https://www.linkedin.com/in/ishan-madhusha-b457921ba/"
                className="text-light fs-4"
                target="_blank"
                rel="noopener noreferrer"
              >
                <FaLinkedin />
              </a>
            </div>
          </Col>
        </Row>
        <hr className="border-secondary mt-2 mb-2" />
        <div className="text-center mb-1">
          <small className="text-sm">
            &copy; {new Date().getFullYear()} Cart System | Developed by{" "}
            <a
              href="https://github.com/PAIshanMadusha"
              className="text-light text-decoration-none"
            >
              PAIshanMadusha
            </a>
          </small>
        </div>
      </Container>
    </footer>
  );
};

export default Footer;
