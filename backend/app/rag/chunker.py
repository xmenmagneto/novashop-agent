"""Split document text into chunks with metadata."""

from ..config import CHUNK_OVERLAP, CHUNK_SIZE


def chunk_text(text: str, source: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """Split `text` into overlapping chunks of at most `chunk_size` characters.

    Each chunk carries metadata: {"source": source, "text": chunk}.
    """
    chunks = []
    start = 0
    length = len(text)
    step = max(chunk_size - overlap, 1)

    while start < length:
        end = min(start + chunk_size, length)
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({"source": source, "text": chunk_text})
        if end >= length:
            break
        start += step

    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chunk a list of {"source", "content"} docs into a flat list of chunks."""
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_text(doc["content"], doc["source"]))
    return all_chunks
