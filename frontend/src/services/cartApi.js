import { apiRequest } from "./api";

export const cartApi = {
  get: () => apiRequest("/cart"),

  addItem: (productId, quantity = 1) =>
    apiRequest("/cart/items", {
      method: "POST",
      body: JSON.stringify({
        product_id: productId,
        quantity,
      }),
    }),

  updateItem: (itemId, quantity) =>
    apiRequest(`/cart/items/${itemId}`, {
      method: "PATCH",
      body: JSON.stringify({ quantity }),
    }),

  removeItem: (itemId) =>
    apiRequest(`/cart/items/${itemId}`, {
      method: "DELETE",
    }),

  clear: () =>
    apiRequest("/cart", {
      method: "DELETE",
    }),

  merge: (items) =>
    apiRequest("/cart/merge", {
      method: "POST",
      body: JSON.stringify({ items }),
    }),
};
