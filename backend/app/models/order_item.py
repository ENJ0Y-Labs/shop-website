import uuid

from ..extensions import db


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    order_id = db.Column(db.Uuid, db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = db.Column(db.Uuid, db.ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    product_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.BigInteger, nullable=False)
    subtotal = db.Column(db.BigInteger, nullable=False)

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")
