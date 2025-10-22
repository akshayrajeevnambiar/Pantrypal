import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Approvals() {
  const [pending, setPending] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    try {
      const res = await api("/counts/pending", {
        query: { limit: 50, offset: 0 },
      });
      setPending(res.items || res || []);
      setError("");
    } catch (e) {
      setError(e.message);
    }
  }
  useEffect(() => {
    load();
  }, []);

  async function act(id, action) {
    setBusy(true);
    try {
      const updated = await api(`/counts/${id}/${action}`, { method: "POST" });
      setPending((s) => s.filter((x) => x.id !== updated.id));
    } catch (e) {
      alert(e.message);
    } finally {
      setBusy(false);
    }
  }

  if (error) return <div className="error">{error}</div>;

  return (
    <div className="card">
      <h2>Pending Counts</h2>
      <ul>
        {pending.map((c) => (
          <li key={c.id}>
            {c.item_name}: {c.count} — by {c.submitted_by_name}
            <button
              disabled={busy}
              onClick={() => act(c.id, "approve")}
              style={{ marginLeft: 8 }}
            >
              Approve
            </button>
            <button
              disabled={busy}
              onClick={() => act(c.id, "reject")}
              style={{ marginLeft: 8 }}
            >
              Reject
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
