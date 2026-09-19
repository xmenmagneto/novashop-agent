"""Build system prompts with retrieved knowledge context."""

from ..llm import SYSTEM_PROMPT


def build_system_prompt(context_chunks: list[dict]) -> str:
    """Return a system prompt that includes retrieved knowledge.

    If no relevant chunks were found, instructs the agent to say the
    information is unavailable rather than inventing an answer.
    """
    if not context_chunks:
        return (
            SYSTEM_PROMPT
            + "\n\nNo relevant NovaShop knowledge was found for the user's question. "
            "If the user is asking for company-specific information, clearly say that "
            "the information is unavailable in the NovaShop knowledge base rather than making something up."
        )

    context_block = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in context_chunks
    )
    return (
        SYSTEM_PROMPT
        + "\n\nThe following NovaShop knowledge was retrieved to help answer the user's question. "
        "Use this information when it is relevant. Do not invent policies not present here.\n\n"
        + context_block
    )
