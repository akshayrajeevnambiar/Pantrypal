import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Approvals() {
  const [pending, setPending] = useState([]);
  const [error, setError] = useState("");

  async function load() {
    try {
      const res = await api("/dash/pending-approvals", {
        query: { limit: 50, offset: 0 },
      });
      setPending(Array.isArray(res) ? res : res.items || []);
      setError("");
    } catch (e) {
      setError(e.message);
    }
  }
  useEffect(() => {
    load();
  }, []);

  return (
    <div className="card">
      <h2>Pending Counts</h2>
      {error && <div className="error">{error}</div>}
      <p style={{ opacity: 0.75, marginTop: 0 }}>
        Note: Approve/Reject endpoints are not exposed on this backend build
        yet. Showing the queue read-only.
      </p>
      <ul>
        {pending.map((c) => (
          <li key={c.id}>
            {c.item_name}: {c.count} — by {c.submitted_by_name} —{" "}
            <b>{c.status}</b>
          </li>
        ))}
      </ul>
    </div>
  );
}
