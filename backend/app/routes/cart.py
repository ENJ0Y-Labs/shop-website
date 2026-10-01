from flask import Blueprint, jsonify, request, session

from ..errors import APIError
from ..extensions import db
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


def _current_cart():
    user_id = get_authenticated_user_id(session)
    return get_or_create_cart(user_id)


@cart_bp.get("")
def get_cart():
    return jsonify({"cart": serialize_cart(_current_cart())})


@cart_bp.post("/items")
def create_cart_item():
    data = require_json(request)
    product_id = data.get("product_id")
    if not product_id:
        raise APIError("product_id is required.", 400, "missing_product_id")

    cart = _current_cart()
    add_item(cart, product_id, data.get("quantity", 1))
    db.session.commit()

    return jsonify({"cart": serialize_cart(cart)}), 201


@cart_bp.patch("/items/<item_id>")
def patch_cart_item(item_id):
    data = require_json(request)
    if "quantity" not in data:
        raise APIError("quantity is required.", 400, "missing_quantity")

    cart = _current_cart()
    update_item(cart, item_id, data["quantity"])
    db.session.commit()

    return jsonify({"cart": serialize_cart(cart)})


@cart_bp.delete("/items/<item_id>")
def delete_cart_item(item_id):
    cart = _current_cart()
    remove_item(cart, item_id)
    db.session.commit()

    return jsonify({"cart": serialize_cart(cart)})


@cart_bp.delete("")
def delete_cart():
    cart = _current_cart()
    clear_cart(cart)
    db.session.commit()

    return jsonify({"cart": serialize_cart(cart)})


@cart_bp.post("/merge")
def merge_cart():
    data = require_json(request)
    cart = _current_cart()
    merge_items(cart, data.get("items", []))
    db.session.commit()

    return jsonify({"cart": serialize_cart(cart)})
