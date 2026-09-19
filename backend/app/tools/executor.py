"""Dispatch OpenAI tool calls to the corresponding backend functions."""

import json

from .functions import check_availability, create_ticket, look_up_order

# Map tool name -> callable.
_TOOL_HANDLERS = {
    "look_up_order": look_up_order,
    "check_availability": check_availability,
    "create_ticket": create_ticket,
}


def execute_tool(name: str, arguments: str) -> str:
    """Execute a tool by name with JSON-string arguments.

    Returns the tool result as a JSON string (so it can be passed back to
    OpenAI as a tool message).
    """
    handler = _TOOL_HANDLERS.get(name)
    if handler is None:
        return json.dumps({"error": f"Unknown tool: {name}"})

    try:
        args = json.loads(arguments) if arguments else {}
    except json.JSONDecodeError:
        return json.dumps({"error": f"Invalid arguments for tool {name}: {arguments}"})

    try:
        result = handler(**args)
    except TypeError as exc:
        return json.dumps({"error": f"Invalid arguments for tool {name}: {exc}"})

    return json.dumps(result)
