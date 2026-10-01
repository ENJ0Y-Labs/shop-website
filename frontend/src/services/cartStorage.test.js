import assert from "node:assert/strict";
import test from "node:test";

class MemoryStorage {
  #store = new Map();

  getItem(key) {
    return this.#store.has(key) ? this.#store.get(key) : null;
  }

  setItem(key, value) {
    this.#store.set(key, String(value));
  }

  removeItem(key) {
    this.#store.delete(key);
  }
}

globalThis.localStorage = new MemoryStorage();

const {
  addToLocalCart,
  clearLocalCart,
  getLocalCart,
  hasLocalCartItems,
  removeFromLocalCart,
  updateLocalCartItem,
} = await import("./cartStorage.js");

test("visitor cart persists, updates, removes, and clears items", () => {
  clearLocalCart();

  assert.deepEqual(getLocalCart(), []);
  assert.equal(hasLocalCartItems(), false);

  addToLocalCart("product-a", 2);
  addToLocalCart("product-a", 1);
  addToLocalCart("product-b", 1);

  assert.deepEqual(getLocalCart(), [
    { product_id: "product-a", quantity: 3 },
    { product_id: "product-b", quantity: 1 },
  ]);
  assert.equal(hasLocalCartItems(), true);

  updateLocalCartItem("product-a", 4);
  assert.deepEqual(getLocalCart(), [
    { product_id: "product-a", quantity: 4 },
    { product_id: "product-b", quantity: 1 },
  ]);

  removeFromLocalCart("product-b");
  assert.deepEqual(getLocalCart(), [
    { product_id: "product-a", quantity: 4 },
  ]);

  clearLocalCart();
  assert.deepEqual(getLocalCart(), []);
  assert.equal(hasLocalCartItems(), false);
});

test("visitor cart rejects malformed stored data", () => {
  localStorage.setItem("enj0y_cart", JSON.stringify([
    { product_id: "valid", quantity: 2 },
    { product_id: "", quantity: 3 },
    { product_id: "bad-quantity", quantity: 0 },
    { product_id: "also-bad", quantity: "two" },
  ]));

  assert.deepEqual(getLocalCart(), [
    { product_id: "valid", quantity: 2 },
  ]);

  clearLocalCart();
});
