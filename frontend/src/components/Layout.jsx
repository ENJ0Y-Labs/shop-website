import { useEffect, useState } from "react";

import { useAuth } from "../context/AuthContext";
import { CartBadge, navigate } from "./RouteView";

export default function Layout({ children }) {
  const { user, isAuthenticated, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  function go(path) {
    navigate(path);
    setMenuOpen(false);
  }

  useEffect(() => {
    const close = () => setMenuOpen(false);
    window.addEventListener("popstate", close);
    return () => window.removeEventListener("popstate", close);
  }, []);

  async function handleLogout() {
    await logout();
    go("/");
  }

  return (
    <div className="site">
      <header className="site-header">
        <div className="container nav">
          <button className="brand" onClick={() => go("/")} aria-label="Go to shop">
            <span className="brand-mark">e</span>
            <span>enj0y <strong>Solution</strong></span>
          </button>

          <button
            className="nav-toggle"
            aria-label="Toggle navigation"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((open) => !open)}
          >
            <span /><span /><span />
          </button>

          <nav className={`nav-links ${menuOpen ? "nav-links--open" : ""}`}>
            <button onClick={() => go("/")}>Shop</button>
            <button onClick={() => go("/cart")}>Cart <CartBadge /></button>
            {isAuthenticated && <button onClick={() => go("/orders")}>Orders</button>}
            {isAuthenticated ? (
              <div className="nav-account">
                <span className="nav-user">{user?.name}</span>
                <button className="button button--ghost" onClick={handleLogout}>Log out</button>
              </div>
            ) : (
              <div className="nav-account">
                <button className="button button--ghost" onClick={() => go("/login")}>Log in</button>
                <button className="button button--primary button--small" onClick={() => go("/register")}>Create account</button>
              </div>
            )}
          </nav>
        </div>
      </header>

      <main>{children}</main>

      <footer className="site-footer">
        <div className="container footer-content">
          <span>enj0y Solution</span>
          <span>Built for simple, reliable shopping.</span>
        </div>
      </footer>
    </div>
  );
}
