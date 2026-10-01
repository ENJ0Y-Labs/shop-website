import { useEffect, useState } from "react";

import { PageState, navigate } from "../components/RouteView";
import { useCart } from "../context/CartContext";
import { productApi } from "../services/productApi";

const money = (kobo) => new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN" }).format((kobo ?? 0) / 100);

export default function ProductDetails({ id }) {
  const { addItem } = useCart();
  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    productApi.get(id).then((response) => setProduct(response.product)).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <PageState message="Loading product..." />;
  if (error) return <PageState message={error} error />;
  if (!product) return <PageState message="Product not found." error />;

  function add() {
    addItem(product.id, quantity);
    navigate("/cart");
  }

  return (
    <div className="page-shell">
      <section className="container detail-layout">
        <button className="back-link" onClick={() => navigate("/")}>← Back to shop</button>
        <div className="detail-card">
          <div className="detail-image">
            {product.image_url ? <img src={product.image_url} alt={product.name} /> : <span>{product.name.slice(0, 1)}</span>}
          </div>
          <div className="detail-copy">
            <span className="eyebrow">{product.category || "Shop"}</span>
            <h1>{product.name}</h1>
            <p className="detail-price">{money(product.price)}</p>
            <p className="detail-description">{product.description || "A carefully selected product from the enj0y Solution collection."}</p>
            <p className={product.in_stock ? "stock stock--in" : "stock stock--out"}>{product.in_stock ? `${product.stock} available` : "Currently out of stock"}</p>
            {product.variants && <pre className="variant-box">{JSON.stringify(product.variants, null, 2)}</pre>}
            <div className="purchase-row">
              <input aria-label="Quantity" type="number" min="1" max={Math.max(product.stock, 1)} value={quantity} onChange={(event) => setQuantity(Math.max(1, Number(event.target.value) || 1))} disabled={!product.in_stock} />
              <button className="button button--primary" disabled={!product.in_stock} onClick={add}>{product.in_stock ? "Add to cart" : "Sold out"}</button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
