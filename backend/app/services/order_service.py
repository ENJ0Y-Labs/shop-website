from sqlalchemy import cast, func, Integer, select

from ..errors import APIError
from ..extensions import db
from ..models import Cart, CartItem, Order, OrderItem, Product
from ..utils.validation import required_string, validate_email


def _next_order_number():
    current = db.session.execute(
        select(func.max(cast(func.substr(Order.order_number, 5), Integer)))
    ).scalar_one_or_none()
    return f"ORD-{(current or 0) + 1:06d}"


def _validate_checkout(data):
    if not isinstance(data, dict):
        raise APIError("Request body must be a JSON object.", 400, "invalid_json")

    name = required_string(data, "name", 255)
    email = validate_email(required_string(data, "email", 255))
    phone = required_string(data, "phone", 50)
    address = required_string(data, "address", 500)
    city = required_string(data, "city", 100)
    state = required_string(data, "state", 100)
    country = required_string(data, "country", 100)

    return {
        "customer_name": name,
        "customer_email": email,
        "customer_phone": phone,
        "shipping_address": address,
        "shipping_city": city,
        "shipping_state": state,
        "shipping_country": country,
    }


def serialize_order(order):
    return {
        "id": str(order.id),
        "order_number": order.order_number,
        "status": order.status,
        "total_amount": order.total_amount,
        "customer": {
            "name": order.customer_name,
            "email": order.customer_email,
            "phone": order.customer_phone,
            "address": order.shipping_address,
            "city": order.shipping_city,
            "state": order.shipping_state,
            "country": order.shipping_country,
        },
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "id": str(item.id),
                "product_id": str(item.product_id) if item.product_id else None,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.subtotal,
            }
            for item in order.items
        ],
    }


def create_order(user_id, data):
    checkout = _validate_checkout(data)

    cart = db.session.query(Cart).filter_by(user_id=user_id).first()
    if not cart:
        raise APIError("Your cart is empty.", 400, "empty_cart")

    cart_items = (
        db.session.query(CartItem)
        .filter_by(cart_id=cart.id)
        .order_by(CartItem.product_id.asc())
        .all()
    )
    if not cart_items:
        raise APIError("Your cart is empty.", 400, "empty_cart")

    product_ids = sorted({item.product_id for item in cart_items}, key=str)
    products = (
        db.session.query(Product)
        .filter(Product.id.in_(product_ids))
        .order_by(Product.id.asc())
        .with_for_update()
        .execution_options(populate_existing=True)
        .all()
    )
    products_by_id = {product.id: product for product in products}

    try:
        total = 0
        snapshots = []

        for cart_item in cart_items:
            product = products_by_id.get(cart_item.product_id)
            if not product:
                raise APIError(
                    "One or more products in your cart no longer exist.",
                    409,
                    "product_unavailable",
                )

            if cart_item.quantity > product.stock:
                raise APIError(
                    f"Only {product.stock} unit(s) of {product.name} are available.",
                    409,
                    "insufficient_stock",
                )

            subtotal = product.price * cart_item.quantity
            total += subtotal
            snapshots.append((cart_item, product, subtotal))

        order = Order(
            user_id=user_id,
            order_number=_next_order_number(),
            total_amount=total,
            status="confirmed",
            **checkout,
        )
        db.session.add(order)
        db.session.flush()

        for cart_item, product, subtotal in snapshots:
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    quantity=cart_item.quantity,
                    unit_price=product.price,
                    subtotal=subtotal,
                )
            )
            product.stock -= cart_item.quantity

        db.session.query(CartItem).filter_by(cart_id=cart.id).delete(
            synchronize_session=False
        )
        db.session.flush()

        return order
    except Exception:
        db.session.rollback()
        raise
