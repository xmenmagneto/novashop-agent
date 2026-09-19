import os

from openai import OpenAI

from .config import CHAT_MODEL, EMBEDDING_MODEL, SYSTEM_PROMPT_PATH

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
