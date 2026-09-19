import os
from pathlib import Path

from openai import OpenAI

# Load environment variables from a local .env file if present.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Load the system prompt from a dedicated file so it is not hardcoded here.
SYSTEM_PROMPT_PATH = Path(__file__).parent / "system_prompt.txt"
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


def chat_with_openai(messages: list[dict]) -> str:
    """Send the conversation history to OpenAI and return the assistant's reply.

    `messages` is a list of {"role": ..., "content": ...} dicts (user/assistant).
    The system prompt is prepended automatically.
    """
    completion = get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
    )
    return completion.choices[0].message.content
