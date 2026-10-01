import html
import logging

import requests
from flask import current_app

logger = logging.getLogger(__name__)


def _format_money(amount):
    return f"₦{amount / 100:,.2f}"


def _build_email_content(order):
    order_number = order.order_number
    customer_name = html.escape(order.customer_name)
    order_date = order.created_at.strftime("%Y-%m-%d %H:%M UTC")
    status = html.escape(order.status)

    text_lines = [
        f"Order confirmation: {order_number}",
        "",
        f"Customer: {order.customer_name}",
        f"Order date: {order_date}",
        f"Order status: {order.status}",
        "",
        "Products:",
    ]

    item_rows = []
    for item in order.items:
        unit_price = _format_money(item.unit_price)
        subtotal = _format_money(item.subtotal)
        text_lines.append(
            f"- {item.product_name} | Quantity: {item.quantity} | "
            f"Unit price: {unit_price} | Subtotal: {subtotal}"
        )
        item_rows.append(
            "<tr>"
            f"<td>{html.escape(item.product_name)}</td>"
            f"<td>{item.quantity}</td>"
            f"<td>{unit_price}</td>"
            f"<td>{subtotal}</td>"
            "</tr>"
        )

    text_lines.extend(
        [
            "",
            f"Total: {_format_money(order.total_amount)}",
            f"Order status: {order.status}",
        ]
    )

    html_body = f"""
    <!doctype html>
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.5; color: #111;">
        <h2>Order confirmation</h2>
        <p>Thank you, {customer_name}. Your order <strong>{html.escape(order_number)}</strong> has been confirmed.</p>
        <p>
          <strong>Order date:</strong> {html.escape(order_date)}<br>
          <strong>Order status:</strong> {status}
        </p>
        <table cellpadding="8" cellspacing="0" border="1" style="border-collapse: collapse; width: 100%;">
          <thead>
            <tr>
              <th align="left">Product</th>
              <th align="left">Quantity</th>
              <th align="left">Unit price</th>
              <th align="left">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            {''.join(item_rows)}
          </tbody>
        </table>
        <p><strong>Total: {_format_money(order.total_amount)}</strong></p>
        <p>Order status: {status}</p>
      </body>
    </html>
    """

    return "\\n".join(text_lines), html_body


def send_order_confirmation(order):
    """Send an order confirmation after the order transaction has committed.

    Email delivery is deliberately best-effort. A Mailgun failure is logged and
    does not roll back an already committed order.
    """
    api_key = current_app.config.get("MAILGUN_API_KEY")
    domain = current_app.config.get("MAILGUN_DOMAIN")
    from_email = current_app.config.get("MAILGUN_FROM_EMAIL")

    if not all((api_key, domain, from_email)):
        logger.warning(
            "Mailgun is not configured; confirmation email skipped for order %s",
            order.order_number,
        )
        return False

    base_url = current_app.config.get(
        "MAILGUN_API_BASE_URL", "https://api.mailgun.net"
    ).rstrip("/")
    url = f"{base_url}/v3/{domain}/messages"
    text_body, html_body = _build_email_content(order)

    try:
        response = requests.post(
            url,
            auth=("api", api_key),
            data={
                "from": from_email,
                "to": order.customer_email,
                "subject": f"Order confirmation - {order.order_number}",
                "text": text_body,
                "html": html_body,
                "o:tag": "order-confirmation",
            },
            timeout=current_app.config.get("MAILGUN_TIMEOUT", 10),
        )
        response.raise_for_status()
    except requests.RequestException:
        logger.exception(
            "Mailgun confirmation email failed for order %s",
            order.order_number,
        )
        return False

    logger.info(
        "Mailgun confirmation email queued for order %s",
        order.order_number,
    )
    return True
