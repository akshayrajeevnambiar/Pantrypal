// frontend/src/components/Navbar.jsx
import { Link, useNavigate } from "react-router-dom";
import { logout } from "../lib/auth";

export default function Navbar({ user, setUser }) {
  const nav = useNavigate();
  async function onLogout() {
    await logout();
    setUser(null);
    nav("/");
  }
  const role = user?.role;

  return (
    <nav className="nav">
      <Link to="/" className="brand">
        PantryPal
      </Link>
      <div className="grow" />
      {user ? (
        <>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/items">Items</Link>
          <Link to="/counts">Counts</Link>
          {(role === "manager" || role === "admin") && (
            <Link to="/approvals">Approvals</Link>
          )}
          <Link to="/billing">Billing</Link>
          <span className="user">
            {user.email} ({role})
          </span>
          <button onClick={onLogout}>Logout</button>
        </>
      ) : (
        <Link to="/login" className="primary">
          Login
        </Link>
      )}
    </nav>
  );
}
