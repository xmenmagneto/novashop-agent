"""In-memory vector store for document chunks."""

import math


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors (no numpy dependency)."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorStore:
    """A minimal in-memory vector store.

    Stores a list of chunk dicts, each with keys: source, text, embedding.
    """

    def __init__(self):
        self._chunks: list[dict] = []

    def add(self, chunks: list[dict]) -> None:
        self._chunks.extend(chunks)

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[tuple[dict, float]]:
        """Return the top_k most similar (chunk, score) pairs, highest score first."""
        scored = [
            (chunk, cosine_similarity(query_embedding, chunk["embedding"]))
            for chunk in self._chunks
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def __len__(self) -> int:
        return len(self._chunks)
