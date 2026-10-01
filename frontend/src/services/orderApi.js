const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  const payload = response.status === 204 ? null : await response.json();

  if (!response.ok) {
    const error = new Error(payload?.error?.message ?? "Request failed.");
    error.status = response.status;
    error.code = payload?.error?.code;
    throw error;
  }

  return payload;
}

export const orderApi = {
  create: (checkout) =>
    request("/orders", {
      method: "POST",
      body: JSON.stringify(checkout),
    }),
};
