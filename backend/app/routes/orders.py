from flask import Blueprint, jsonify, request, session

from ..extensions import db
from ..services.cart_service import get_authenticated_user_id
from ..services.mail_service import send_order_confirmation
from ..services.order_service import (
    create_order,
    get_user_order,
    get_user_orders,
    serialize_order,
)
from ..utils.validation import require_json

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@orders_bp.get("")
def list_orders():
    user_id = get_authenticated_user_id(session)
    orders = get_user_orders(user_id)
    return jsonify({"orders": [serialize_order(order) for order in orders]})


@orders_bp.get("/<order_id>")
def get_order(order_id):
    user_id = get_authenticated_user_id(session)
    order = get_user_order(user_id, order_id)
    return jsonify({"order": serialize_order(order)})


@orders_bp.post("")
def create_order_route():
    user_id = get_authenticated_user_id(session)
    data = require_json(request)

    order = create_order(user_id, data)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    send_order_confirmation(order)
    return jsonify({"order": serialize_order(order)}), 201
