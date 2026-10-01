import uuid

from sqlalchemy import select

from ..errors import APIError
from ..extensions import db
from ..models import Cart, CartItem, Product


def get_authenticated_user_id(session):
    user_id = session.get("user_id")
    if not user_id:
        raise APIError("Authentication required.", 401, "unauthenticated")

    try:
        return uuid.UUID(str(user_id))
    except (ValueError, AttributeError):
        session.clear()
        raise APIError("Authentication required.", 401, "unauthenticated")


def get_or_create_cart(user_id):
    cart = db.session.query(Cart).filter_by(user_id=user_id).first()
    if cart:
        return cart

    cart = Cart(user_id=user_id)
    db.session.add(cart)
    db.session.flush()
    return cart


def _serialize_item(item):
    product = item.product
    subtotal = product.price * item.quantity

    return {
        "id": str(item.id),
        "product": {
            "id": str(product.id),
            "name": product.name,
            "price": product.price,
            "image_url": product.image_url,
            "category": product.category,
            "stock": product.stock,
            "in_stock": product.stock > 0,
            "variants": product.variants,
        },
        "quantity": item.quantity,
        "subtotal": subtotal,
    }


def serialize_cart(cart):
    items = [_serialize_item(item) for item in cart.items]
    return {
        "id": str(cart.id),
        "items": items,
        "total": sum(item["subtotal"] for item in items),
        "item_count": sum(item["quantity"] for item in items),
    }


def _parse_uuid(value, field_name):
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        raise APIError(f"Invalid {field_name}.", 400, "invalid_product_id")


def _parse_quantity(value):
    if isinstance(value, bool):
        raise APIError("Quantity must be a positive integer.", 400, "invalid_quantity")

    try:
        quantity = int(value)
    except (TypeError, ValueError):
        raise APIError("Quantity must be a positive integer.", 400, "invalid_quantity")

    if quantity < 1:
        raise APIError("Quantity must be a positive integer.", 400, "invalid_quantity")

    return quantity


def add_item(cart, product_id, quantity):
    product_uuid = _parse_uuid(product_id, "product ID")
    quantity = _parse_quantity(quantity)

    product = db.session.get(Product, product_uuid)
    if not product:
        raise APIError("Product not found.", 404, "product_not_found")

    item = (
        db.session.query(CartItem)
        .filter_by(cart_id=cart.id, product_id=product.id)
        .first()
    )
    new_quantity = quantity + item.quantity if item else quantity

    if new_quantity > product.stock:
        raise APIError(
            f"Only {product.stock} unit(s) of this product are available.",
            409,
            "insufficient_stock",
        )

    if item:
        item.quantity = new_quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
        db.session.add(item)

    db.session.flush()
    return item


def update_item(cart, item_id, quantity):
    item_uuid = _parse_uuid(item_id, "cart item ID")
    quantity = _parse_quantity(quantity)

    item = (
        db.session.query(CartItem)
        .filter_by(id=item_uuid, cart_id=cart.id)
        .first()
    )
    if not item:
        raise APIError("Cart item not found.", 404, "cart_item_not_found")

    if quantity > item.product.stock:
        raise APIError(
            f"Only {item.product.stock} unit(s) of this product are available.",
            409,
            "insufficient_stock",
        )

    item.quantity = quantity
    db.session.flush()
    return item


def remove_item(cart, item_id):
    item_uuid = _parse_uuid(item_id, "cart item ID")
    item = (
        db.session.query(CartItem)
        .filter_by(id=item_uuid, cart_id=cart.id)
        .first()
    )
    if not item:
        raise APIError("Cart item not found.", 404, "cart_item_not_found")

    db.session.delete(item)
    db.session.flush()


def clear_cart(cart):
    db.session.query(CartItem).filter_by(cart_id=cart.id).delete(
        synchronize_session=False
    )
    db.session.flush()


def merge_items(cart, items):
    if not isinstance(items, list):
        raise APIError("Items must be an array.", 400, "invalid_items")

    requested = {}
    for entry in items:
        if not isinstance(entry, dict):
            raise APIError("Each cart item must be an object.", 400, "invalid_items")

        product_id = entry.get("product_id")
        if product_id is None:
            raise APIError("Each cart item requires a product_id.", 400, "invalid_items")

        product_uuid = _parse_uuid(product_id, "product ID")
        quantity = _parse_quantity(entry.get("quantity"))
        requested[product_uuid] = requested.get(product_uuid, 0) + quantity

    if not requested:
        return

    products = {
        product.id: product
        for product in db.session.scalars(
            select(Product).where(Product.id.in_(requested.keys()))
        ).all()
    }

    missing = [product_id for product_id in requested if product_id not in products]
    if missing:
        raise APIError("One or more products were not found.", 404, "product_not_found")

    existing = {
        item.product_id: item
        for item in db.session.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id.in_(requested.keys()),
        )
        .all()
    }

    for product_id, requested_quantity in requested.items():
        product = products[product_id]
        current_quantity = existing[product_id].quantity if product_id in existing else 0
        merged_quantity = current_quantity + requested_quantity

        if merged_quantity > product.stock:
            raise APIError(
                f"Only {product.stock} unit(s) of {product.name} are available.",
                409,
                "insufficient_stock",
            )

    for product_id, requested_quantity in requested.items():
        item = existing.get(product_id)
        if item:
            item.quantity += requested_quantity
        else:
            db.session.add(
                CartItem(
                    cart_id=cart.id,
                    product_id=product_id,
                    quantity=requested_quantity,
                )
            )

    db.session.flush()
