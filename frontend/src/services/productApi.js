import { apiRequest } from "./api";

export const productApi = {
  list: (params = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") query.set(key, value);
    });
    return apiRequest(`/products?${query.toString()}`);
  },
  get: (id) => apiRequest(`/products/${id}`),
};
