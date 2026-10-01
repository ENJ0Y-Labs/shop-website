import uuid
from datetime import datetime, timezone

from ..extensions import db


class Order(db.Model):
    __tablename__ = "orders"
    __table_args__ = (
        db.CheckConstraint("total_amount >= 0", name="ck_orders_total_nonnegative"),
    )

    id = db.Column(db.Uuid, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.Uuid, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    order_number = db.Column(db.String(32), nullable=False, unique=True)
    total_amount = db.Column(db.BigInteger, nullable=False)
    status = db.Column(db.String(32), nullable=False, default="pending")
    customer_name = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(255), nullable=False)
    customer_phone = db.Column(db.String(50), nullable=False)
    shipping_address = db.Column(db.String(500), nullable=False)
    shipping_city = db.Column(db.String(100), nullable=False)
    shipping_state = db.Column(db.String(100), nullable=False)
    shipping_country = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
