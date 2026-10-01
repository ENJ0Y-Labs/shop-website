import { useEffect, useState } from "react";

import ProductCard from "../components/ProductCard";
import { EmptyState, PageState, navigate } from "../components/RouteView";
import { useCart } from "../context/CartContext";
import { productApi } from "../services/productApi";

export default function Shop() {
  const { addItem } = useCart();
  const [products, setProducts] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("name");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const timer = setTimeout(async () => {
      setLoading(true);
      setError("");
      try {
        const response = await productApi.list({ search, sort, per_page: 12 });
        setProducts(response.products);
        setPagination(response.pagination);
      } catch (requestError) {
        setError(requestError.message);
      } finally {
        setLoading(false);
      }
    }, 180);
    return () => clearTimeout(timer);
  }, [search, sort]);

  return (
    <div className="page-shell">
      <section className="hero">
        <div className="container hero-inner">
          <div>
            <span className="eyebrow">enj0y Solution / Shop</span>
            <h1>Useful things.<br /><span>Simply chosen.</span></h1>
            <p>Browse the collection, add what you need, and check out without the circus.</p>
          </div>
          <button className="hero-action" onClick={() => navigate("/cart")}>View cart</button>
        </div>
      </section>

      <section className="container shop-section">
        <div className="section-heading">
          <div><span className="eyebrow">Collection</span><h2>Shop all products</h2></div>
          <div className="shop-controls">
            <label className="search-field">
              <span className="sr-only">Search products</span>
              <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search products..." />
            </label>
            <select value={sort} onChange={(event) => setSort(event.target.value)} aria-label="Sort products">
              <option value="name">Name</option>
              <option value="price_asc">Price: low to high</option>
              <option value="price_desc">Price: high to low</option>
            </select>
          </div>
        </div>

        {loading && <PageState message="Loading products..." />}
        {!loading && error && <PageState message={error} error />}
        {!loading && !error && products.length === 0 && <EmptyState title="Nothing matched." message="Try a different search." />}
        {!loading && !error && products.length > 0 && (
          <>
            <div className="product-grid">{products.map((product) => <ProductCard key={product.id} product={product} onAdd={() => addItem(product.id, 1)} />)}</div>
            {pagination && <p className="results-count">{pagination.total} product{pagination.total === 1 ? "" : "s"}</p>}
          </>
        )}
      </section>
    </div>
  );
}
