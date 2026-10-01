"""add checkout customer details to orders

Revision ID: 0003_checkout_customer_details
Revises: 0002_product_variants
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_checkout_customer_details"
down_revision = "0002_product_variants"
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = (
        ("customer_name", sa.String(length=255)),
        ("customer_email", sa.String(length=255)),
        ("customer_phone", sa.String(length=50)),
        ("shipping_address", sa.String(length=500)),
        ("shipping_city", sa.String(length=100)),
        ("shipping_state", sa.String(length=100)),
        ("shipping_country", sa.String(length=100)),
    )

    for name, column_type in columns:
        op.add_column("orders", sa.Column(name, column_type, nullable=True))

    op.execute(
        """
        UPDATE orders
        SET customer_name = users.name,
            customer_email = users.email,
            customer_phone = '',
            shipping_address = '',
            shipping_city = '',
            shipping_state = '',
            shipping_country = ''
        FROM users
        WHERE orders.user_id = users.id
        """
    )

    for name, column_type in columns:
        op.alter_column(
            "orders",
            name,
            existing_type=column_type,
            nullable=False,
        )


def downgrade() -> None:
    for name, _ in (
        ("shipping_country", sa.String(length=100)),
        ("shipping_state", sa.String(length=100)),
        ("shipping_city", sa.String(length=100)),
        ("shipping_address", sa.String(length=500)),
        ("customer_phone", sa.String(length=50)),
        ("customer_email", sa.String(length=255)),
        ("customer_name", sa.String(length=255)),
    ):
        op.drop_column("orders", name)
