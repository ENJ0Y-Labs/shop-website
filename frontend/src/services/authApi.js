import { apiRequest, API_BASE_URL } from "./api";

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
  googleLoginUrl: () => `${API_BASE_URL}/auth/google`,
};
