import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { cartApi } from "../services/cartApi";
import {
  addToLocalCart,
  clearLocalCart,
  getLocalCart,
  hasLocalCartItems,
  removeFromLocalCart,
  setLocalCart,
  updateLocalCartItem,
} from "../services/cartStorage";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [authenticated, setAuthenticated] = useState(false);
  const [cart, setCart] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadCart() {
      try {
        const response = await cartApi.get();
        if (!cancelled) {
          setAuthenticated(true);
          setCart(response.cart);
        }
      } catch {
        if (!cancelled) {
          setAuthenticated(false);
          setCart(null);
        }
      }
    }

    loadCart();

    return () => {
      cancelled = true;
    };
  }, []);

  async function syncAfterLogin() {
    const localItems = getLocalCart();

    if (localItems.length) {
      const response = await cartApi.merge(localItems);
      clearLocalCart();
      setCart(response.cart);
      setAuthenticated(true);
      return response.cart;
    }

    const response = await cartApi.get();
    setCart(response.cart);
    setAuthenticated(true);
    return response.cart;
  }

  function addVisitorItem(productId, quantity = 1) {
    const items = addToLocalCart(productId, quantity);
    setCart({ items, item_count: items.reduce((sum, item) => sum + item.quantity, 0), total: null });
    return items;
  }

  function updateVisitorItem(productId, quantity) {
    const items = updateLocalCartItem(productId, quantity);
    setCart({ items, item_count: items.reduce((sum, item) => sum + item.quantity, 0), total: null });
    return items;
  }

  function removeVisitorItem(productId) {
    const items = removeFromLocalCart(productId);
    setCart({ items, item_count: items.reduce((sum, item) => sum + item.quantity, 0), total: null });
    return items;
  }

  function clearVisitorCart() {
    clearLocalCart();
    setCart({ items: [], item_count: 0, total: 0 });
  }

  const value = useMemo(
    () => ({
      cart,
      authenticated,
      hasLocalItems: hasLocalCartItems(),
      syncAfterLogin,
      addVisitorItem,
      updateVisitorItem,
      removeVisitorItem,
      clearVisitorCart,
      setLocalCart,
    }),
    [cart, authenticated],
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
}
