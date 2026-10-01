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
    const message = payload?.error?.message ?? "Cart request failed.";
    throw new Error(message);
  }

  return payload;
}

export const cartApi = {
  get: () => request("/cart"),

  addItem: (productId, quantity = 1) =>
    request("/cart/items", {
      method: "POST",
      body: JSON.stringify({
        product_id: productId,
        quantity,
      }),
    }),

  updateItem: (itemId, quantity) =>
    request(`/cart/items/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify({ quantity }),
    }),

  removeItem: (itemId) =>
    request(`/cart/items/${itemId}`, {
      method: "DELETE",
    }),

  clear: () =>
    request("/cart", {
      method: "DELETE",
    }),

  merge: (items) =>
    request("/cart/merge", {
      method: "POST",
      body: JSON.stringify({ items }),
    }),
};
