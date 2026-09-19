import logging
import os

from openai import OpenAI

from .config import CHAT_MODEL, EMBEDDING_MODEL, SYSTEM_PROMPT_PATH
from .tools.definitions import TOOLS
from .tools.executor import execute_tool

logger = logging.getLogger("novashop.llm")

# Load environment variables from a local .env file if present.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Load the system prompt from a dedicated file so it is not hardcoded here.
SYSTEM_PROMPT = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()

_client: OpenAI | None = None

# User-friendly fallback returned when the OpenAI API is unreachable.
_API_UNAVAILABLE_MSG = (
    "I'm having trouble connecting to the AI service right now. "
    "Please try again in a moment, or I can create a support ticket for you."
)


def get_client() -> OpenAI:
    """Lazily create the OpenAI client so the app can boot without a key."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please set it in the environment or in backend/.env."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def embed_text(text: str) -> list[float]:
    """Return the embedding vector for the given text."""
    response = get_client().embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def chat_with_openai(messages: list[dict], system_prompt: str = SYSTEM_PROMPT) -> str:
    """Send the conversation history to OpenAI and return the assistant's reply.

    `messages` is a list of {"role": ..., "content": ...} dicts (user/assistant).
    The system prompt is prepended automatically. Pass `system_prompt` to override
    the default (e.g., to inject retrieved knowledge into the system context).

    If the OpenAI API call fails, a user-friendly fallback message is returned
    instead of raising.
    """
    try:
        completion = get_client().chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "system", "content": system_prompt}, *messages],
        )
        return completion.choices[0].message.content or ""
    except Exception as exc:  # noqa: BLE001 — log the real error, return safe text
        logger.exception("OpenAI chat completion failed")
        return _API_UNAVAILABLE_MSG


def chat_with_tools_stream(messages: list[dict], system_prompt: str = SYSTEM_PROMPT):
    """Generator version of chat_with_tools that streams the final response.

    The tool-calling loop runs synchronously (tools are fast and the user sees
    a "thinking" indicator). Once the model is ready to produce a final text
    answer, that answer is streamed token-by-token back to the caller.

    Yields:
        str: incremental pieces of the assistant's final response text.
    """
    conversation = [{"role": "system", "content": system_prompt}, *messages]

    while True:
        try:
            completion = get_client().chat.completions.create(
                model=CHAT_MODEL,
                messages=conversation,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception:  # noqa: BLE001 — log the real error, return safe text
            logger.exception("OpenAI chat completion (with tools) failed")
            yield _API_UNAVAILABLE_MSG
            return

        message = completion.choices[0].message

        # If the model did not call any tool, we have the final answer.
        # Re-issue the call with stream=True so the caller gets tokens live.
        if not message.tool_calls:
            try:
                stream = get_client().chat.completions.create(
                    model=CHAT_MODEL,
                    messages=conversation,
                    stream=True,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
            except Exception:  # noqa: BLE001
                logger.exception("OpenAI streaming completion failed")
                yield _API_UNAVAILABLE_MSG
            return

        # Append the assistant's tool-call message to the conversation.
        conversation.append(message)

        # Execute each requested tool and append the results.
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            arguments = tool_call.function.arguments
            result = execute_tool(name, arguments)
            conversation.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": name,
                "content": result,
            })


def chat_with_tools(messages: list[dict], system_prompt: str = SYSTEM_PROMPT) -> str:
    """Chat with OpenAI using native tool calling. Returns the full final reply.

    This is a convenience wrapper around chat_with_tools_stream that collects
    all streamed tokens into a single string.
    """
    return "".join(chat_with_tools_stream(messages, system_prompt=system_prompt))
