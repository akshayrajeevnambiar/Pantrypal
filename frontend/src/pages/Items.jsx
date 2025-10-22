import { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";

export default function Items({ user }) {
  const canWrite = user?.role === "manager" || user?.role === "admin";

  const [items, setItems] = useState([]);
  const [q, setQ] = useState("");
  const [activeOnly, setActiveOnly] = useState(true);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const res = await api("/items", {
        query: {
          q: q || undefined,
          active: activeOnly || undefined,
          limit: 50,
          offset: 0,
        },
      });
      setItems(res.items || []);
      setError("");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    load();
  }, []);

  const list = useMemo(() => items, [items]);

  async function addItem() {
    if (!canWrite) return alert("Insufficient privileges");
    const name = prompt("Item name?");
    if (!name) return;
    const base_unit = prompt("Base unit? (g/ml/pcs)", "pcs") || "pcs";
    const par_level = Number(prompt("Par level?", "10") || "10");
    try {
      const created = await api("/items", {
        method: "POST",
        body: { name, base_unit, par_level },
      });
      setItems((prev) => [created, ...prev]);
    } catch (e) {
      alert(e.message);
    }
  }

  async function updatePar(it, v) {
    if (!canWrite) return alert("Insufficient privileges");
    try {
      const updated = await api(`/items/${it.id}`, {
        method: "PUT",
        body: { par_level: Number(v) },
      });
      setItems((s) => s.map((x) => (x.id === updated.id ? updated : x)));
    } catch (e) {
      alert(e.message);
    }
  }

  async function softDelete(it) {
    if (!canWrite) return alert("Insufficient privileges");
    if (!confirm(`Soft delete "${it.name}"?`)) return;
    try {
      await api(`/items/${it.id}`, { method: "DELETE" });
      activeOnly
        ? setItems((s) => s.filter((x) => x.id !== it.id))
        : setItems((s) =>
            s.map((x) => (x.id === it.id ? { ...x, is_active: false } : x))
          );
    } catch (e) {
      alert(e.message);
    }
  }

  async function restore(it) {
    if (!canWrite) return alert("Insufficient privileges");
    try {
      const restored = await api(`/items/${it.id}/restore`, { method: "POST" });
      setItems((s) => s.map((x) => (x.id === restored.id ? restored : x)));
    } catch (e) {
      alert(e.message);
    }
  }

  return (
    <div>
      <div className="row">
        <input
          placeholder="Search name..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <label>
          <input
            type="checkbox"
            checked={activeOnly}
            onChange={(e) => setActiveOnly(e.target.checked)}
          />{" "}
          Active only
        </label>
        <button className="primary" onClick={load}>
          Search
        </button>
        {canWrite && <button onClick={addItem}>Add Item</button>}
      </div>
      {error && <div className="error">{error}</div>}
      {loading ? (
        <div>Loading…</div>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Unit</th>
              <th>Par</th>
              <th>Current</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {list.map((it) => (
              <tr key={it.id}>
                <td>{it.name}</td>
                <td>{it.base_unit}</td>
                <td>
                  {canWrite ? (
                    <input
                      type="number"
                      value={it.par_level}
                      onChange={(e) => updatePar(it, e.target.value)}
                    />
                  ) : (
                    <span>{it.par_level}</span>
                  )}
                </td>
                <td>{it.current_qty}</td>
                <td>
                  {it.is_active ? (it.is_below_par ? "LOW" : "OK") : "INACTIVE"}
                </td>
                <td>
                  {canWrite &&
                    (it.is_active ? (
                      <button onClick={() => softDelete(it)}>Delete</button>
                    ) : (
                      <button onClick={() => restore(it)}>Restore</button>
                    ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
