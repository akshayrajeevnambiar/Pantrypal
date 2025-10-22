import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Counts() {
  const [items, setItems] = useState([]);
  const [mine, setMine] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    try {
      const list = await api("/items", {
        query: { active: true, limit: 100, offset: 0 },
      });
      setItems(list.items || []);
      const counts = await api("/counts", {
        query: {
          mine: true,
          status_filter: statusFilter || undefined,
          limit: 50,
          offset: 0,
        },
      });
      setMine(counts.items || counts || []);
      setError("");
    } catch (e) {
      setError(e.message);
    }
  }
  useEffect(() => {
    load();
  }, []);
  useEffect(() => {
    load();
  }, [statusFilter]);

  async function submit(itemId) {
    const val = prompt("Enter count value:");
    if (val === null) return;
    const count = Number(val);
    if (Number.isNaN(count)) return alert("Invalid number");
    setBusy(true);
    try {
      await api("/counts/submit", {
        method: "POST",
        body: { item_id: itemId, count },
      });
      await load();
    } catch (e) {
      alert(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid">
      <div className="card">
        <h3>Submit Count</h3>
        {error && <div className="error">{error}</div>}
        <ul>
          {items.map((it) => (
            <li key={it.id}>
              {it.name} — current {it.current_qty} {it.base_unit}
              <button
                disabled={busy}
                onClick={() => submit(it.id)}
                style={{ marginLeft: 8 }}
              >
                Submit
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="card">
        <h3>My Submissions</h3>
        <div className="row">
          <label>
            Status:&nbsp;
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">all</option>
              <option value="pending">pending</option>
              <option value="approved">approved</option>
              <option value="rejected">rejected</option>
            </select>
          </label>
        </div>
        <ul>
          {mine.map((c) => (
            <li key={c.id}>
              {c.item_name}: {c.count} — <b>{c.status}</b> (
              {c.submitted_by_name})
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
