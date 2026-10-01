import { useEffect, useMemo, useState } from "react";

import { useCart } from "../context/CartContext";
import { orderApi } from "../services/orderApi";

const initialForm = {
  name: "",
  email: "",
  phone: "",
  address: "",
  city: "",
  state: "",
  country: "Nigeria",
};

const money = (kobo) =>
  new Intl.NumberFormat("en-NG", {
    style: "currency",
    currency: "NGN",
  }).format((kobo ?? 0) / 100);

export default function Checkout() {
  const { cart, authenticated } = useCart();
  const [form, setForm] = useState(initialForm);
  const [authChecked, setAuthChecked] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [order, setOrder] = useState(null);

  useEffect(() => {
    const apiBase = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5000/api";

    fetch(`${apiBase}/auth/me`, { credentials: "include" })
      .then((response) => {
        if (!response.ok) throw new Error("Authentication required.");
        return response.json();
      })
      .then(({ user }) => {
        setForm((current) => ({
          ...current,
          name: user.name ?? "",
          email: user.email ?? "",
        }));
      })
      .catch(() => setError("You must be signed in before you can place an order."))
      .finally(() => setAuthChecked(true));
  }, []);

  const total = useMemo(() => cart?.total ?? 0, [cart]);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (!authenticated) {
      setError("You must be signed in before you can place an order.");
      return;
    }

    if (!cart?.items?.length) {
      setError("Your cart is empty.");
      return;
    }

    setSubmitting(true);

    try {
      const response = await orderApi.create(form);
      setOrder(response.order);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (order) {
    return (
      <main className="checkout-page">
        <section className="checkout-card">
          <p className="checkout-eyebrow">Order confirmed</p>
          <h1>Thank you, {order.customer.name}.</h1>
          <p>
            Your order <strong>{order.order_number}</strong> has been confirmed.
          </p>
          <p>Total: <strong>{money(order.total_amount)}</strong></p>
        </section>
      </main>
    );
  }

  if (!authChecked) {
    return (
      <main className="checkout-page">
        <section className="checkout-card">
          <p>Checking your session...</p>
        </section>
      </main>
    );
  }

  return (
    <main className="checkout-page">
      <section className="checkout-card">
        <div>
          <p className="checkout-eyebrow">Checkout</p>
          <h1>Complete your order</h1>
          <p className="checkout-muted">
            Your final price, stock, and order total are verified by the server.
          </p>
        </div>

        {error && <p className="checkout-error" role="alert">{error}</p>}

        <form onSubmit={handleSubmit} className="checkout-form">
          <label>
            Full name
            <input name="name" value={form.name} onChange={handleChange} required maxLength={255} />
          </label>

          <label>
            Email
            <input name="email" type="email" value={form.email} onChange={handleChange} required maxLength={255} />
          </label>

          <label>
            Phone
            <input name="phone" value={form.phone} onChange={handleChange} required maxLength={50} />
          </label>

          <label>
            Address
            <input name="address" value={form.address} onChange={handleChange} required maxLength={500} />
          </label>

          <div className="checkout-grid">
            <label>
              City
              <input name="city" value={form.city} onChange={handleChange} required maxLength={100} />
            </label>

            <label>
              State
              <input name="state" value={form.state} onChange={handleChange} required maxLength={100} />
            </label>
          </div>

          <label>
            Country
            <input name="country" value={form.country} onChange={handleChange} required maxLength={100} />
          </label>

          <div className="checkout-summary">
            <span>Current cart total</span>
            <strong>{money(total)}</strong>
          </div>

          <button type="submit" disabled={submitting || !authenticated || !cart?.items?.length}>
            {submitting ? "Placing order..." : "Place order"}
          </button>
        </form>
      </section>
    </main>
  );
}
