"""OpenAI tool definitions (schemas) for the NovaShop agent."""

TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "look_up_order",
            "description": (
                "Look up information about a NovaShop customer order. "
                "Use this when the customer asks about a specific order and provides an order ID "
                "(for example NS-10234), or asks about the status, tracking, or delivery of an order."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The NovaShop order ID, for example NS-10234",
                    }
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": (
                "Check whether a NovaShop product is currently in stock. "
                "Use this when the customer asks if a product is available, in stock, "
                "or how many units are left."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the NovaShop product, for example Nova Pro Keyboard",
                    }
                },
                "required": ["product_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": (
                "Create a customer support ticket for an issue that requires human support. "
                "Use this when the customer reports a problem, complaint, or issue that cannot be "
                "resolved with information alone, and asks for support or help from a representative."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "A short summary of the customer's issue or request",
                    }
                },
                "required": ["summary"],
            },
        },
    },
]
