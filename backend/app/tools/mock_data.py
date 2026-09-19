"""Mock business data for NovaShop tools (orders, products, tickets)."""

# --- Mock orders ---
ORDERS: dict[str, dict] = {
    "NS-10234": {
        "order_id": "NS-10234",
        "product": "Nova Headphones",
        "quantity": 1,
        "status": "shipped",
        "carrier": "FedEx",
        "estimated_delivery": "2026-09-21",
    },
    "NS-10235": {
        "order_id": "NS-10235",
        "product": "Nova Pro Keyboard",
        "quantity": 1,
        "status": "processing",
        "carrier": None,
        "estimated_delivery": "2026-09-23",
    },
    "NS-10236": {
        "order_id": "NS-10236",
        "product": "Nova 4K Monitor",
        "quantity": 2,
        "status": "delivered",
        "carrier": "UPS",
        "estimated_delivery": "2026-09-15",
    },
}

# --- Mock product inventory ---
PRODUCTS: dict[str, dict] = {
    "Nova Headphones": {"available": True, "stock": 18},
    "Nova Pro Keyboard": {"available": True, "stock": 24},
    "Nova 4K Monitor": {"available": False, "stock": 0},
    "Nova Wireless Mouse": {"available": True, "stock": 42},
}
