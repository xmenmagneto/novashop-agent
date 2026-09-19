"""Tool implementations for the NovaShop agent.

Each function takes simple arguments and returns a JSON-serializable result.
The agent uses OpenAI tool calling to decide when to invoke these.

Business-logic "not found" cases return an {"error": ...} dict so the LLM can
report it honestly. Unexpected exceptions are caught by the executor.
"""

import logging
import random

from .mock_data import ORDERS, PRODUCTS

logger = logging.getLogger("novashop.tools")

# In-memory ticket storage (resets on server restart).
_tickets: list[dict] = []


def look_up_order(order_id: str) -> dict:
    """Return order details for the given order ID, or an error if not found."""
    order = ORDERS.get(order_id)
    if order is None:
        logger.info("Order lookup failed: order %s not found", order_id)
        return {"error": f"Order {order_id} could not be found."}
    return order


def check_availability(product_name: str) -> dict:
    """Return availability and stock for a product, or an error if not found."""
    product = PRODUCTS.get(product_name)
    if product is None:
        logger.info("Availability check failed: product '%s' not found", product_name)
        return {"error": f"Product '{product_name}' could not be found."}
    return {"product": product_name, **product}


def create_ticket(summary: str) -> dict:
    """Create a support ticket and return its ID."""
    try:
        ticket_id = f"TICKET-{random.randint(1000, 9999)}"
        ticket = {"ticket_id": ticket_id, "summary": summary, "status": "created"}
        _tickets.append(ticket)
        logger.info("Created support ticket %s", ticket_id)
        return ticket
    except Exception as exc:  # noqa: BLE001
        # Re-raise so the executor can log and return a safe error to the LLM.
        logger.exception("create_ticket failed")
        raise
