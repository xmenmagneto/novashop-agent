"""Load Markdown documents from the knowledge directory."""

from pathlib import Path

from ..config import KNOWLEDGE_DIR


def load_documents(knowledge_dir: Path = KNOWLEDGE_DIR) -> list[dict]:
    """Return a list of {"source": filename, "content": text} for every .md file."""
    docs = []
    for path in sorted(knowledge_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        if content:
            docs.append({"source": path.name, "content": content})
    return docs
