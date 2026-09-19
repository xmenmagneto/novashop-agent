"""Create embeddings for text chunks using the OpenAI API."""

from ..llm import embed_text


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Add an "embedding" field to each chunk dict.

    Each chunk must have a "text" key. Returns the same list with embeddings added.
    """
    for chunk in chunks:
        chunk["embedding"] = embed_text(chunk["text"])
    return chunks
