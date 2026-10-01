from flask import Blueprint, jsonify, request

from ..errors import APIError
from ..services.cart_service import (
    add_item,
    clear_cart,
    get_authenticated_user_id,
    get_or_create_cart,
    merge_items,
    remove_item,
    serialize_cart,
    update_item,
)
from ..utils.validation import require_json


cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")


def _cart_for_request():
    user_id = get_authenticated_user_id(request.environ.get("flask.session"))
    return get_or_create_cart(user_id)


@cart_bp.get("")
def get_cart():
    from flask import session

    cart = get_or_create_cart(get_authenticated_user_id(session))
    return jsonify({"cart": serialize_cart(cart)})


@cart_bp.post("/items")
def create_cart_item():
    from flask import session

    data = require_json(request)
    product_id = data.get("product_id")
    if not product_id:
        raise APIError("product_id is required.", 400, "missing_product_id")

    quantity = data.get("quantity", 1)
    user_id = get_authenticated_user_id(session)
    cart = get_or_create_cart(user_id)

    add_item(cart, product_id, quantity)
    db_commit = __import__("backend.app.extensions", fromlist=["db"]).db
    db_commit.session.commit()

    return jsonify({"cart": serialize_cart(cart)}), 201


@cart_bp.patch("/items/<item_id>")
def patch_cart_item(item_id):
    from flask import session

    data = require_json(request)
    if "quantity" not in data:
        raise APIError("quantity is required.", 400, "missing_quantity")

    user_id = get_authenticated_user_id(session)
    cart = get_or_create_cart(user_id)
    update_item(cart, item_id, data["quantity"])

    db_commit = __import__("backend.app.extensions", fromlist=["db"]).db
    db_commit.session.commit()
    return jsonify({"cart": serialize_cart(cart)})


@cart_bp.delete("/items/<item_id>")
def delete_cart_item(item_id):
    from flask import session

    user_id = get_authenticated_user_id(session)
    cart = get_or_create_cart(user_id)
    remove_item(cart, item_id)

    db_commit = __import__("backend.app.extensions", fromlist=["db"]).db
    db_commit.session.commit()
    return jsonify({"cart": serialize_cart(cart)})


@cart_bp.delete("")
def delete_cart():
    from flask import session

    user_id = get_authenticated_user_id(session)
    cart = get_or_create_cart(user_id)
    clear_cart(cart)

    db_commit = __import__("backend.app.extensions", fromlist=["db"]).db
    db_commit.session.commit()
    return jsonify({"cart": serialize_cart(cart)})


@cart_bp.post("/merge")
def merge_cart():
    from flask import session

    data = require_json(request)
    user_id = get_authenticated_user_id(session)
    cart = get_or_create_cart(user_id)

    merge_items(cart, data.get("items", []))

    db_commit = __import__("backend.app.extensions", fromlist=["db"]).db
    db_commit.session.commit()
    return jsonify({"cart": serialize_cart(cart)})
