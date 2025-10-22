// frontend/src/pages/Landing.jsx
import { Link } from "react-router-dom";

export default function Landing({ user }) {
  return (
    <div className="hero">
      <h1>PantryPal</h1>
      <p>Simple inventory + count approvals for small teams.</p>
      {user ? (
        <Link to="/dashboard" className="primary">
          Open Dashboard
        </Link>
      ) : (
        <Link to="/login" className="primary">
          Get Started
        </Link>
      )}
    </div>
  );
}
