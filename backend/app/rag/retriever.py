"""Retrieve relevant knowledge chunks for a user query."""

from ..config import SIMILARITY_THRESHOLD, TOP_K
from ..llm import embed_text
from .vector_store import VectorStore


class Retriever:
    """Embed the user query and return relevant chunks from the vector store."""

    def __init__(self, store: VectorStore, top_k: int = TOP_K, threshold: float = SIMILARITY_THRESHOLD):
        self.store = store
        self.top_k = top_k
        self.threshold = threshold

    def retrieve(self, query: str) -> list[dict]:
        """Return chunks whose similarity exceeds the threshold.

        Each returned chunk has keys: source, text, score.
        Returns an empty list if no chunk is similar enough.
        """
        if len(self.store) == 0:
            return []

        query_embedding = embed_text(query)
        results = self.store.search(query_embedding, top_k=self.top_k)

        relevant = []
        for chunk, score in results:
            if score >= self.threshold:
                relevant.append({
                    "source": chunk["source"],
                    "text": chunk["text"],
                    "score": score,
                })
        return relevant
