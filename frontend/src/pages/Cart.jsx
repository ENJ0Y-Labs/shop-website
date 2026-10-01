import { useEffect, useMemo, useState } from "react";

import { EmptyState, PageState, navigate } from "../components/RouteView";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { cartApi } from "../services/cartApi";
import { productApi } from "../services/productApi";

const money = (kobo) => new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format((kobo ?? 0) / 100);

export default function Cart() {
  const { cart, authenticated, updateVisitorItem, removeVisitorItem, clearVisitorCart } = useCart();
  const { isAuthenticated } = useAuth();
  const [products, setProducts] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function hydrate() {
      if (!cart?.items?.length) { setLoading(false); return; }
      try {
        const entries = await Promise.all(cart.items.map(async (item) => {
          const id = item.product_id ?? item.product?.id;
          if (item.product) return [id, item.product];
          const response = await productApi.get(id);
          return [id, response.product];
        }));
        setProducts(Object.fromEntries(entries));
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }
    hydrate();
  }, [cart?.items]);

  const total = useMemo(() => {
    if (authenticated && cart?.total != null) return cart.total;
    return cart?.items?.reduce((sum, item) => {
      const product = products[item.product_id];
      return sum + (product?.price ?? 0) * item.quantity;
    }, 0) ?? 0;
  }, [authenticated, cart, products]);

  async function update(item, quantity) {
    if (quantity < 1) return remove(item);
    if (authenticated) {
      await cartApi.updateItem(item.id, quantity);
      window.dispatchEvent(new Event("cart-refresh"));
    } else updateVisitorItem(item.product_id, quantity);
  }

  async function remove(item) {
    if (authenticated) {
      await cartApi.removeItem(item.id);
      window.dispatchEvent(new Event("cart-refresh"));
    } else removeVisitorItem(item.product_id);
  }

  async function clear() {
    if (authenticated) {
      await cartApi.clear();
      window.dispatchEvent(new Event("cart-refresh"));
    } else clearVisitorCart();
  }

  if (loading) return <PageState message="Loading your cart..." />;
  if (error) return <PageState message={error} error />;
  if (!cart?.items?.length) return <div className="page-shell"><section className="container content-narrow"><EmptyState title="Your cart is empty." message="There is nothing to check out yet." action={() => navigate("/")} actionLabel="Continue shopping" /></section></div>;

  return (
    <div className="page-shell">
      <section className="container content-narrow">
        <div className="section-heading"><div><span className="eyebrow">Cart</span><h1>Your selection</h1></div><button className="text-button" onClick={clear}>Clear cart</button></div>
        <div className="cart-list">
          {cart.items.map((item) => {
            const id = item.product_id ?? item.product?.id;
            const product = item.product ?? products[id];
            if (!product) return null;
            return (
              <article className="cart-row" key={item.id ?? id}>
                <div className="cart-row__image">{product.image_url ? <img src={product.image_url} alt="" /> : <span>{product.name.slice(0, 1)}</span>}</div>
                <div className="cart-row__info"><button className="cart-product-name" onClick={() => navigate(`/products/${id}`)}>{product.name}</button><span>{money(product.price)}</span></div>
                <div className="quantity-control"><button onClick={() => update(item, item.quantity - 1)} aria-label="Decrease quantity">−</button><span>{item.quantity}</span><button onClick={() => update(item, item.quantity + 1)} aria-label="Increase quantity">+</button></div>
                <button className="remove-button" onClick={() => remove(item)}>Remove</button>
              </article>
            );
          })}
        </div>
        <div className="cart-summary"><span>Total</span><strong>{money(total)}</strong></div>
        <div className="cart-actions">
          <button className="button button--ghost" onClick={() => navigate("/")}>Continue shopping</button>
          {isAuthenticated ? <button className="button button--primary" onClick={() => navigate("/checkout")}>Checkout</button> : <button className="button button--primary" onClick={() => navigate("/login?next=/checkout")}>Sign in to checkout</button>}
        </div>
      </section>
    </div>
  );
}
