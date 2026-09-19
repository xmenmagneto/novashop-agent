import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .agent.agent import Agent
from .rag.chunker import chunk_documents
from .rag.embeddings import embed_chunks
from .rag.loader import load_documents
from .rag.retriever import Retriever
from .rag.vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("novashop")

app = FastAPI(title="NovaShop Customer Support AI Agent")

# Allow the Next.js dev server to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The agent is created during startup after the vector store is built.
_agent: Agent | None = None


def init_knowledge_base() -> Agent:
    """Load documents, chunk, embed, build the vector store, and return an Agent."""
    logger.info("Initializing NovaShop knowledge base...")
    documents = load_documents()
    logger.info("Loaded %d document(s)", len(documents))

    chunks = chunk_documents(documents)
    logger.info("Chunked into %d chunk(s)", len(chunks))

    embed_chunks(chunks)
    logger.info("Generated embeddings for %d chunk(s)", len(chunks))

    store = VectorStore()
    store.add(chunks)

    retriever = Retriever(store)
    logger.info("Knowledge base ready")
    return Agent(retriever)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _agent
    try:
        _agent = init_knowledge_base()
    except Exception as exc:  # noqa: BLE001
        # Don't crash the server if the KB fails to load (e.g., no API key).
        logger.warning("Knowledge base initialization failed: %s", exc)
        logger.warning("Running without RAG. Agent will not use retrieved knowledge.")
        _agent = None
    yield


app.router.lifespan_context = lifespan


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str
    sources: list[str] = Field(default_factory=list)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    messages_dicts = [m.model_dump() for m in request.messages]

    try:
        if _agent is None:
            # Fallback: no RAG, but tools still work.
            from .llm import chat_with_tools
            reply = chat_with_tools(messages_dicts)
            return ChatResponse(response=reply, sources=[])

        reply, sources = _agent.reply(messages_dicts)
    except RuntimeError as exc:
        # Missing API key etc. — log the detail, return a safe message.
        logger.exception("Runtime error handling chat request")
        raise HTTPException(
            status_code=500,
            detail="The service is not configured correctly. Please contact support.",
        ) from exc
    except Exception as exc:  # noqa: BLE001
        # Log the full error for debugging; never expose internals to the client.
        logger.exception("Unexpected error handling chat request")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while processing your request. Please try again later.",
        ) from exc

    return ChatResponse(response=reply, sources=sources)
