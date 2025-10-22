import { api, setToken } from "./api";

export const whoami = async () => api("/auth/whoami"); // returns user object

export const login = async (email, password) => {
  const res = await api("/auth/login", {
    method: "POST",
    body: { email, password },
  });
  if (!res.access_token) throw new Error("Missing access token");
  setToken(res.access_token); // <-- localStorage: pp_token
  const user = await whoami(); // <-- now fetch the user
  if (!user || !user.id) throw new Error("Failed to load user profile");
  return { user };
};

export const logout = async () => {
  setToken("");
  return { ok: true };
};
