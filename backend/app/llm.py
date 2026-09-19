import os

from openai import OpenAI

# Load environment variables from a local .env file if present.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

SYSTEM_PROMPT = (
    "You are NovaShop's customer support assistant. "
    "Answer the user's question politely and concisely."
)

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


def chat_with_openai(user_message: str) -> str:
    """Send a user message to OpenAI and return the assistant's reply."""
    completion = get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return completion.choices[0].message.content
