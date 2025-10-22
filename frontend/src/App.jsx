// frontend/src/App.jsx
import { useEffect, useState, useCallback } from "react";
import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Items from "./pages/Items";
import Counts from "./pages/Counts";
import Approvals from "./pages/Approvals";
import Billing from "./pages/Billing";
import { whoami } from "./lib/auth";
import { setToken } from "./lib/api";

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const nav = useNavigate();

  const refreshUser = useCallback(async () => {
    try {
      const me = await whoami();
      setUser(me?.user || null);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const t = sessionStorage.getItem("pp_token");
    if (t) setToken(t);
    refreshUser();
  }, [refreshUser]);

  if (loading) return <div className="center">Loading…</div>;

  return (
    <div className="container">
      <Navbar user={user} setUser={setUser} />
      <Routes>
        <Route path="/" element={<Landing user={user} />} />
        <Route
          path="/login"
          element={
            user ? <Navigate to="/dashboard" /> : <Login setUser={setUser} />
          }
        />
        <Route
          path="/dashboard"
          element={
            <Protected user={user}>
              <Dashboard />
            </Protected>
          }
        />
        <Route
          path="/items"
          element={
            <Protected user={user}>
              <Items />
            </Protected>
          }
        />
        <Route
          path="/counts"
          element={
            <Protected user={user}>
              <Counts user={user} />
            </Protected>
          }
        />
        <Route
          path="/approvals"
          element={
            <Protected user={user}>
              <Approvals user={user} />
            </Protected>
          }
        />
        <Route
          path="/billing"
          element={
            <Protected user={user}>
              <Billing user={user} onStatusChange={refreshUser} />
            </Protected>
          }
        />
        <Route path="*" element={<div>Not found</div>} />
      </Routes>
    </div>
  );
}

function Protected({ user, children }) {
  if (!user) return <Navigate to="/login" />;
  return children;
}
