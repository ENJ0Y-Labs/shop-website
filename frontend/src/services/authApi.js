import { apiRequest } from "./api";

export const authApi = {
  me: () => apiRequest("/auth/me"),
  login: (credentials) => apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  }),
  register: (data) => apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  }),
  logout: () => apiRequest("/auth/logout", { method: "POST" }),
  googleLoginUrl: () => {
    const base = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000/api";
    return `${base}/auth/google`;
  },
};
