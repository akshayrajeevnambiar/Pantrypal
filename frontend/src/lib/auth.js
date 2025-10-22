// frontend/src/lib/auth.js
import { api, setToken } from "./api";

export const whoami = () => api("/auth/whoami");

export const login = async (email, password) => {
  // Expecting backend response: { access_token, token_type, user }
  const res = await api("/auth/login", {
    method: "POST",
    body: { email, password },
  });
  const token = res.access_token || res.token;
  if (!token) throw new Error("Missing token");
  setToken(token);
  sessionStorage.setItem("pp_token", token);
  return { user: res.user };
};

export const logout = async () => {
  sessionStorage.removeItem("pp_token");
  setToken("");
  return { ok: true };
};
