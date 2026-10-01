const CART_STORAGE_KEY = "enj0y_cart";

function normalizeItem(item) {
  if (!item || typeof item !== "object") return null;

  const productId = String(item.product_id ?? item.product?.id ?? "");
  const quantity = Number(item.quantity);

  if (!productId || !Number.isInteger(quantity) || quantity < 1) {
    return null;
  }

  return { product_id: productId, quantity };
}

export function getLocalCart() {
  try {
    const raw = localStorage.getItem(CART_STORAGE_KEY);
    if (!raw) return [];

    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];

    return parsed.map(normalizeItem).filter(Boolean);
  } catch {
    return [];
  }
}

export function setLocalCart(items) {
  const normalized = Array.isArray(items)
    ? items.map(normalizeItem).filter(Boolean)
    : [];

  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(normalized));
}

export function addToLocalCart(productId, quantity = 1) {
  const items = getLocalCart();
  const existing = items.find((item) => item.product_id === String(productId));

  if (existing) {
    existing.quantity += quantity;
  } else {
    items.push({ product_id: String(productId), quantity });
  }

  setLocalCart(items);
  return items;
}

export function updateLocalCartItem(productId, quantity) {
  const items = getLocalCart().map((item) =>
    item.product_id === String(productId)
      ? { ...item, quantity }
      : item,
  );

  setLocalCart(items.filter((item) => item.quantity > 0));
  return getLocalCart();
}

export function removeFromLocalCart(productId) {
  setLocalCart(
    getLocalCart().filter((item) => item.product_id !== String(productId)),
  );
  return getLocalCart();
}

export function clearLocalCart() {
  localStorage.removeItem(CART_STORAGE_KEY);
}

export function hasLocalCartItems() {
  return getLocalCart().length > 0;
}
