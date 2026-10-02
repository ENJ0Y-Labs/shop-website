import { apiRequest } from "./api";

export const orderApi = {
  create: (checkout) =>
    apiRequest("/orders", {
      method: "POST",
      body: JSON.stringify(checkout),
    }),

  list: () => apiRequest("/orders"),

  get: (id) => apiRequest(`/orders/${id}`),
};
