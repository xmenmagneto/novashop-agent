"""Central configuration for the NovaShop agent and RAG pipeline."""

from pathlib import Path

# --- Paths ---
APP_DIR = Path(__file__).parent
KNOWLEDGE_DIR = APP_DIR.parent.parent / "knowledge"
SYSTEM_PROMPT_PATH = APP_DIR / "system_prompt.txt"

# --- Models ---
CHAT_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# --- RAG ---
CHUNK_SIZE = 500          # max characters per chunk
CHUNK_OVERLAP = 50        # overlap between consecutive chunks
TOP_K = 3                 # number of chunks to retrieve
SIMILARITY_THRESHOLD = 0.50  # min cosine similarity to consider a chunk relevant
