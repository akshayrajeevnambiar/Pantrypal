// frontend/src/lib/api.js
const BASE = import.meta.env.VITE_API_BASE;
let TOKEN = "";

export function setToken(t) {
  TOKEN = t || "";
}

export async function api(path, { method = "GET", body, headers = {} } = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(TOKEN ? { Authorization: `Bearer ${TOKEN}` } : {}),
      ...headers,
    },
    credentials: "include", // harmless with FastAPI CORS
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      msg = err.detail || err.message || msg;
    } catch (_) {}
    throw new Error(msg);
  }
  try {
    return await res.json();
  } catch {
    return {};
  }
}
