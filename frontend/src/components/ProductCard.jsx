import { navigate } from "./RouteView";

const money = (kobo) => new Intl.NumberFormat("en-NG", {
  style: "currency",
  currency: "NGN",
}).format((kobo ?? 0) / 100);

export default function ProductCard({ product, onAdd }) {
  return (
    <article className="product-card">
      <button className="product-card__image" onClick={() => navigate(`/products/${product.id}`)} aria-label={`View ${product.name}`}>
        {product.image_url ? <img src={product.image_url} alt={product.name} /> : <span>{product.name.slice(0, 1)}</span>}
      </button>
      <div className="product-card__body">
        <span className="eyebrow">{product.category || "Shop"}</span>
        <button className="product-card__name" onClick={() => navigate(`/products/${product.id}`)}>{product.name}</button>
        <div className="product-card__bottom">
          <strong>{money(product.price)}</strong>
          <button className="button button--primary button--small" disabled={!product.in_stock} onClick={() => onAdd(product)}>
            {product.in_stock ? "Add to cart" : "Sold out"}
          </button>
        </div>
      </div>
    </article>
  );
}
