import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Dashboard({ user }) {
  const [low, setLow] = useState([]);
  const [pending, setPending] = useState([]);
  const [mine, setMine] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const lowRes = await api("/dash/low-stock");
        setLow(Array.isArray(lowRes) ? lowRes : lowRes.items || []);
      } catch (e) {
        setError(e.message);
      }

      try {
        // manager/admin only; counters will get 403 → we silently ignore
        const pendRes = await api("/dash/pending-approvals", {
          query: { limit: 10, offset: 0 },
        });
        setPending(Array.isArray(pendRes) ? pendRes : pendRes.items || []);
      } catch (e) {
        if (String(e.message).includes("403")) setPending([]);
        else setError(e.message);
      }

      try {
        const mineRes = await api("/dash/my-submissions", {
          query: { status_filter: "" },
        });
        setMine(Array.isArray(mineRes) ? mineRes : mineRes.items || []);
      } catch (e) {
        setError(e.message);
      }
    })();
  }, []);

  if (error && !String(error).includes("403"))
    return <div className="error">{error}</div>;

  return (
    <div className="grid">
      <div className="card">
        <h3>Low stock</h3>
        <p>{low.length} item(s) below par</p>
      </div>
      {(user?.role === "manager" || user?.role === "admin") && (
        <div className="card">
          <h3>Pending approvals</h3>
          <p>{pending.length} awaiting review</p>
        </div>
      )}
      <div className="card">
        <h3>My submissions</h3>
        <p>{mine.length} total</p>
      </div>
    </div>
  );
}
