"""The NovaShop support agent: RAG retrieval + conversation response."""

from ..llm import chat_with_openai
from ..rag.retriever import Retriever
from .prompts import build_system_prompt


class Agent:
    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    def reply(self, messages: list[dict]) -> tuple[str, list[str]]:
        """Generate an assistant reply given the conversation history.

        Returns (response_text, source_filenames).
        `messages` is a list of {"role", "content"} dicts (user/assistant turns).
        """
        # Build a retrieval query from the latest user message plus the previous
        # user turn (if any). This gives the embedder enough context to resolve
        # vague follow-ups like "How long does the standard option take?" that
        # only make sense in light of an earlier message (e.g. about shipping).
        retrieval_query = self._build_retrieval_query(messages)

        context_chunks: list[dict] = []
        sources: list[str] = []

        if retrieval_query:
            try:
                context_chunks = self.retriever.retrieve(retrieval_query)
                sources = list(dict.fromkeys(c["source"] for c in context_chunks))
            except Exception:
                # If retrieval fails (e.g., embedding API error), continue without context.
                context_chunks = []
                sources = []

        system_prompt = build_system_prompt(context_chunks)
        response = chat_with_openai(messages, system_prompt=system_prompt)
        return response, sources

    @staticmethod
    def _build_retrieval_query(messages: list[dict]) -> str:
        """Concatenate the latest two user messages for retrieval.

        The latest message is the primary query; the immediately preceding
        user message adds context so that ambiguous follow-up questions can be
        resolved against the right topic.
        """
        user_messages = [m.get("content", "") for m in messages if m.get("role") == "user" and m.get("content")]
        if not user_messages:
            return ""
        last_two = user_messages[-2:]
        return " ".join(last_two).strip()
