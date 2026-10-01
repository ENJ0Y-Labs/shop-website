import { useEffect, useState } from "react";

import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export function navigate(path) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
  window.scrollTo({ top: 0, behavior: "smooth" });
}

export function RouteView({ children }) {
  const [path, setPath] = useState(window.location.pathname);

  useEffect(() => {
    const onPopState = () => setPath(window.location.pathname);
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  return children(path);
}

export function ProtectedRoute({ children }) {
  const { loading, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!loading && !isAuthenticated) navigate(`/login?next=${encodeURIComponent(window.location.pathname)}`);
  }, [loading, isAuthenticated]);

  if (loading) return <PageState message="Checking your account..." />;
  if (!isAuthenticated) return <PageState message="Redirecting to sign in..." />;

  return children;
}

export function PageState({ message, error = false }) {
  return (
    <main className="page-shell">
      <section className={`state-card ${error ? "state-card--error" : ""}`} role={error ? "alert" : undefined}>
        <p>{message}</p>
      </section>
    </main>
  );
}

export function EmptyState({ title, message, action, actionLabel }) {
  return (
    <section className="empty-state">
      <span className="empty-state__icon" aria-hidden="true">∅</span>
      <h2>{title}</h2>
      <p>{message}</p>
      {action && <button className="button button--primary" onClick={action}>{actionLabel}</button>}
    </section>
  );
}

export function CartBadge() {
  const { cart } = useCart();
  return <span className="cart-badge">{cart?.item_count ?? 0}</span>;
}
