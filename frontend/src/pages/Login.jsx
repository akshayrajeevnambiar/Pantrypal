// frontend/src/pages/Login.jsx
import { useState } from "react";
import { login } from "../lib/auth";
import { useNavigate } from "react-router-dom";

export default function Login({ setUser }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const nav = useNavigate();

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      const res = await login(email, password);
      setUser(res.user);
      nav("/dashboard");
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <form className="card" onSubmit={onSubmit}>
      <h2>Log in</h2>
      {error && <div className="error">{error}</div>}
      <input
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        placeholder="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit" className="primary">
        Login
      </button>
    </form>
  );
}
