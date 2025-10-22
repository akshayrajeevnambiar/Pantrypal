import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Dashboard() {
  const [low, setLow] = useState([]);
  const [pending, setPending] = useState([]);
  const [mine, setMine] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const lowRes = await api("/dash/low-stock");
        const pendRes = await api("/dash/pending-approvals", {
          query: { limit: 10, offset: 0 },
        });
        const mineRes = await api("/dash/my-submissions", {
          query: { status_filter: "" },
        });
        setLow(Array.isArray(lowRes) ? lowRes : lowRes.items || []);
        setPending(Array.isArray(pendRes) ? pendRes : pendRes.items || []);
        setMine(Array.isArray(mineRes) ? mineRes : mineRes.items || []);
      } catch (e) {
        setError(e.message);
      }
    })();
  }, []);

  if (error) return <div className="error">{error}</div>;
  return (
    <div className="grid">
      <div className="card">
        <h3>Low stock</h3>
        <p>{low.length} item(s) below par</p>
      </div>
      <div className="card">
        <h3>Pending approvals</h3>
        <p>{pending.length} awaiting review</p>
      </div>
      <div className="card">
        <h3>My submissions</h3>
        <p>{mine.length} total</p>
      </div>
    </div>
  );
}
