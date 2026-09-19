import os

from openai import OpenAI

from .config import CHAT_MODEL, EMBEDDING_MODEL, SYSTEM_PROMPT_PATH
from .tools.definitions import TOOLS
from .tools.executor import execute_tool

# Load environment variables from a local .env file if present.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Load the system prompt from a dedicated file so it is not hardcoded here.
SYSTEM_PROMPT = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()

_client: OpenAI | None = None


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
    """
    completion = get_client().chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "system", "content": system_prompt}, *messages],
    )
    return completion.choices[0].message.content


def chat_with_tools(messages: list[dict], system_prompt: str = SYSTEM_PROMPT) -> str:
    """Chat with OpenAI using native tool calling.

    Runs the normal tool-call loop:
      1. Send messages + tools to the model.
      2. If the model requests tool calls, execute them and append the results.
      3. Repeat until the model returns a final text response.
      4. Return the final assistant message content.

    Multiple tool calls in a single turn are supported.
    """
    conversation = [{"role": "system", "content": system_prompt}, *messages]

    while True:
        completion = get_client().chat.completions.create(
            model=CHAT_MODEL,
            messages=conversation,
            tools=TOOLS,
            tool_choice="auto",
        )
        message = completion.choices[0].message

        # If the model did not call any tool, we have the final answer.
        if not message.tool_calls:
            return message.content or ""

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
