"""The NovaShop support agent: RAG retrieval + tool calling + conversation response."""

from ..llm import chat_with_tools
from ..rag.retriever import Retriever
from .prompts import build_system_prompt


class Agent:
    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    def reply(self, messages: list[dict]) -> tuple[str, list[str]]:
        """Generate an assistant reply given the conversation history.

        Returns (response_text, source_filenames).
        `messages` is a list of {"role", "content"} dicts (user/assistant turns).

        The agent combines two information sources:
        - RAG: retrieved knowledge base chunks injected into the system prompt.
        - Tools: OpenAI native function calling for live/mock business data.
        """
        context_chunks, sources = self.retrieve_context(messages)
        system_prompt = build_system_prompt(context_chunks)

        # Use the tool-calling chat so the LLM can decide whether to call a tool.
        response = chat_with_tools(messages, system_prompt=system_prompt)
        return response, sources

    def retrieve_context(self, messages: list[dict]) -> tuple[list[dict], list[str]]:
        """Run RAG retrieval for the streaming path.

        Returns (context_chunks, source_filenames).
        Used by the /chat/stream endpoint so RAG results can be sent to the
        client while the LLM response is streamed.
        """
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

        return context_chunks, sources

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
