"""Dispatch OpenAI tool calls to the corresponding backend functions.

All tool execution errors are caught, logged, and returned to the LLM as a
safe JSON error object so the agent never claims an action succeeded when it
actually failed.
"""

import json
import logging

from .functions import check_availability, create_ticket, look_up_order

logger = logging.getLogger("novashop.tools")

# Map tool name -> callable.
_TOOL_HANDLERS = {
    "look_up_order": look_up_order,
    "check_availability": check_availability,
    "create_ticket": create_ticket,
}


def execute_tool(name: str, arguments: str) -> str:
    """Execute a tool by name with JSON-string arguments.

    Returns the tool result as a JSON string (so it can be passed back to
    OpenAI as a tool message). Any exception is caught, logged, and returned
    as a safe error object — no stack traces or internals leak to the LLM.
    """
    handler = _TOOL_HANDLERS.get(name)
    if handler is None:
        logger.warning("Unknown tool requested: %s", name)
        return json.dumps({"error": f"Unknown tool: {name}"})

    try:
        args = json.loads(arguments) if arguments else {}
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON arguments for tool %s: %s", name, exc)
        return json.dumps({"error": f"Invalid arguments for tool {name}."})

    try:
        result = handler(**args)
    except TypeError as exc:
        # Wrong/ missing arguments — this is a model-argument issue, not a system failure.
        logger.warning("Invalid arguments for tool %s: %s", name, exc)
        return json.dumps({"error": f"Invalid arguments for tool {name}."})
    except Exception as exc:  # noqa: BLE001 — catch everything to keep the agent resilient
        # Log the full error for debugging, but return a safe message to the LLM.
        logger.exception("Tool %s failed", name)
        return json.dumps({
            "error": f"Unable to complete the action '{name}' right now. Please try again later.",
        })

    return json.dumps(result)
