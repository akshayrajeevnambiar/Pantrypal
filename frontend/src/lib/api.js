const BASE = import.meta.env.VITE_API_BASE;

export function getToken() {
  return localStorage.getItem("pp_token") || "";
}
export function setToken(t) {
  if (!t) localStorage.removeItem("pp_token");
  else localStorage.setItem("pp_token", t);
}

export async function api(
  path,
  { method = "GET", body, headers = {}, query } = {}
) {
  const token = getToken();
  const url = `${BASE}${path}${buildQS(query)}`;

  const res = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return { ok: true };

  if (res.status === 401) {
    setToken("");
    let msg = "Unauthorized";
    try {
      const err = await res.json();
      msg = err.detail || err.message || msg;
    } catch {}
    window.location.assign("/login");
    throw new Error(msg);
  }

  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      msg = err.detail || err.message || msg;
    } catch {}
    throw new Error(msg);
  }

  try {
    return await res.json();
  } catch {
    return {};
  }
}

function buildQS(params = {}) {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params || {})) {
    if (v === undefined || v === null || v === "") continue;
    q.set(k, String(v));
  }
  const s = q.toString();
  return s ? `?${s}` : "";
}
