from uuid import UUID

from ..errors import APIError
from ..models import Product


ALLOWED_SORTS = {
    "name": Product.name.asc(),
    "price_asc": Product.price.asc(),
    "price_desc": Product.price.desc(),
}


def parse_product_id(product_id):
    try:
        return UUID(product_id)
    except (ValueError, AttributeError):
        raise APIError("Invalid product ID.", 400, "invalid_product_id")


def serialize_product(product, image_url=None):
    return {
        "id": str(product.id),
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "image_url": image_url if image_url is not None else product.image_url,
        "category": product.category,
        "stock": product.stock,
        "in_stock": product.stock > 0,
        "variants": product.variants,
        "created_at": product.created_at.isoformat(),
        "updated_at": product.updated_at.isoformat(),
    }
