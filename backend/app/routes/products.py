from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import or_

from ..errors import APIError
from ..models import Product
from ..services.product_service import ALLOWED_SORTS, parse_product_id, serialize_product


products_bp = Blueprint("products", __name__, url_prefix="/api/products")


def _product_image_url(product):
    image = product.image_url
    if not image:
        return None

    if image.startswith(("http://", "https://")):
        return image

    supabase_url = current_app.config.get("SUPABASE_URL")
    bucket = current_app.config.get("SUPABASE_STORAGE_BUCKET", "product-images")
    if not supabase_url:
        return image

    return f"{supabase_url.rstrip('/')}/storage/v1/object/public/{bucket}/{image.lstrip('/')}"


def _positive_int(value, default, maximum):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise APIError("Pagination values must be integers.", 400, "invalid_pagination")

    if parsed < 1 or parsed > maximum:
        raise APIError(f"Pagination values must be between 1 and {maximum}.", 400, "invalid_pagination")

    return parsed


@products_bp.get("")
def list_products():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "name")
    page = _positive_int(request.args.get("page", 1), 1, 1000000)
    per_page = _positive_int(request.args.get("per_page", 12), 12, 100)

    if sort not in ALLOWED_SORTS:
        raise APIError("Invalid sort option.", 400, "invalid_sort")

    query = Product.query

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(pattern),
                Product.description.ilike(pattern),
            )
        )

    if category:
        query = query.filter(Product.category.ilike(category))

    query = query.order_by(ALLOWED_SORTS[sort], Product.id.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "products": [
            serialize_product(product, _product_image_url(product))
            for product in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_previous": pagination.has_prev,
        },
    })


@products_bp.get("/<product_id>")
def get_product(product_id):
    product_uuid = parse_product_id(product_id)
    product = Product.query.filter_by(id=product_uuid).first()

    if not product:
        raise APIError("Product not found.", 404, "product_not_found")

    return jsonify({
        "product": serialize_product(product, _product_image_url(product))
    })
