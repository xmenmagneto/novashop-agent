# NovaShop Customer Support AI Agent

Nova is an AI-powered customer support agent for **NovaShop**, a fictional e-commerce store selling consumer electronics such as headphones, keyboards, monitors, and accessories.

The goal of this project is to demonstrate a realistic customer-support experience where an AI agent can:

* Answer company-specific questions using a Knowledge Base
* Maintain conversation context within a session
* Look up order information
* Check product availability
* Create support tickets
* Recognize when it does not have enough information
* Gracefully handle errors and escalate to human support
* Stream responses like a real conversational assistant

## Product & Use Case

### Why e-commerce customer support?

E-commerce support naturally combines two types of customer questions:

**Knowledge-based questions**

Examples:

* What is your return policy?
* How long does shipping take?
* What is the warranty?

These are handled through the **Knowledge Base / RAG pipeline**.

**Action-oriented questions**

Examples:

* Where is my order?
* Is this product available?
* I need help from a human.

These require the agent to interact with business systems through **tools**.

This separation makes the prototype feel more like a real support agent rather than a chatbot that simply generates answers.

## Architecture

```text
                        ┌─────────────────────┐
                        │    Next.js Chat UI  │
                        │                     │
                        │ Conversation State  │
                        └──────────┬──────────┘
                                   │
                                   │ POST /chat/stream
                                   ▼
                        ┌─────────────────────┐
                        │    FastAPI Backend  │
                        │                     │
                        │       Agent         │
                        └───────┬─────┬───────┘
                                │     │
                    ┌───────────┘     └────────────┐
                    ▼                              ▼
             ┌─────────────┐                ┌─────────────┐
             │  Knowledge  │                │    Tools    │
             │  Base / RAG │                │             │
             └──────┬──────┘                └──────┬──────┘
                    │                              │
             ┌──────▼──────┐                ┌──────▼─────────┐
             │ Markdown KB │                │ Mock Business  │
             │ Documents   │                │ Data           │
             └─────────────┘                └────────────────┘
                    │
                    ▼
              OpenAI Embeddings

                        ┌─────────────────────┐
                        │      OpenAI LLM     │
                        │     gpt-4o-mini     │
                        └─────────────────────┘
```

### Key Design Decision

The system separates **knowledge retrieval** from **actions**:

* **RAG** provides company knowledge and policies.
* **Tools** provide dynamic business data and perform actions.
* **The LLM** decides when to use the available tools.

This keeps the architecture lightweight while demonstrating core agentic behavior.

## Knowledge Base / RAG

The Knowledge Base contains four Markdown documents:

```text
knowledge/
├── faq.md
├── returns.md
├── shipping.md
└── warranty.md
```

The retrieval pipeline is:

```text
Markdown documents
       ↓
    Chunking
       ↓
OpenAI Embeddings
       ↓
 In-memory Vector Store
       ↓
   Similarity Search
       ↓
 Top 3 relevant chunks
       ↓
   System Prompt
       ↓
      LLM
```

### Implementation

* Embedding model: `text-embedding-3-small`
* Chunk size: 500 characters
* Chunk overlap: 50 characters
* Top-K: 3
* Similarity threshold: 0.50
* Vector store: lightweight in-memory implementation
* Similarity metric: cosine similarity

The Knowledge Base is initialized when the backend starts.

If no sufficiently relevant document is found, the agent is instructed not to invent an answer.

Retrieved source filenames are also returned to the frontend.

## Agent & Tool Calling

Nova uses OpenAI's native tool/function calling.

### Available Tools

#### `look_up_order`

Looks up an order using its order ID.

Example:

```text
NS-10234
```

Returns mock information such as:

* Product
* Quantity
* Order status
* Carrier
* Estimated delivery

#### `check_availability`

Checks mock inventory for a product.

Example:

```text
Nova 4K Monitor
```

Returns:

```json
{
  "product": "Nova 4K Monitor",
  "available": false,
  "stock": 0
}
```

#### `create_ticket`

Creates a mock support ticket and returns a ticket ID.

Example:

```text
TICKET-4821
```

### Tool Calling Flow

```text
User message
     ↓
LLM + tool definitions
     ↓
Does the agent need a tool?
     │
    Yes
     ↓
Tool call
     ↓
Backend executes tool
     ↓
Tool result returned to LLM
     ↓
LLM generates final response
```

The model determines when a tool is appropriate rather than relying on hard-coded keyword routing.

## Conversation Memory

Conversation history is maintained within the current browser session.

The frontend stores the conversation in React state and sends the current conversation history with each request.

The backend remains stateless and sends the conversation history to OpenAI along with the system prompt.

No database or Redis session store is required for this prototype.

This keeps the architecture lightweight while still providing multi-turn conversation behavior.

## Streaming

AI responses are streamed through:

```text
POST /chat/stream
```

The backend returns newline-delimited JSON events:

```json
{"type":"content","text":"..."}
{"type":"content","text":"..."}
{"type":"sources","sources":["shipping.md"]}
```

The frontend reads the response stream and progressively updates the assistant message.

This makes the interaction feel more like a real conversational AI product.

## Graceful Boundaries & Error Handling

The agent is designed not to claim capabilities or actions it cannot perform.

### Unknown Questions

If the Knowledge Base does not contain relevant information, Nova acknowledges the limitation rather than inventing an answer.

### Tool Failures

Tool execution errors are caught by the backend and returned safely to the agent.

The agent does not claim an action succeeded if the underlying tool failed.

### API Failures

OpenAI/API errors are logged server-side while the user receives a friendly error message instead of an internal stack trace.

### Human Handoff

When the issue requires human assistance, Nova can use `create_ticket` to create a support ticket and return the generated ticket ID.

## Tech Stack

### Frontend

* Next.js 14
* React 18
* TypeScript

### Backend

* Python
* FastAPI
* OpenAI Python SDK

### AI

* `gpt-4o-mini`
* `text-embedding-3-small`
* OpenAI native tool/function calling

### Knowledge Retrieval

* Markdown documents
* In-memory vector store
* Cosine similarity

No production database or external vector database is required for this prototype.

## Project Structure

```text
novashop-agent/
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── llm.py
│       ├── system_prompt.txt
│       ├── agent/
│       │   ├── agent.py
│       │   └── prompts.py
│       ├── rag/
│       │   ├── loader.py
│       │   ├── chunker.py
│       │   ├── embeddings.py
│       │   ├── vector_store.py
│       │   └── retriever.py
│       └── tools/
│           ├── definitions.py
│           ├── executor.py
│           ├── functions.py
│           └── mock_data.py
│
├── frontend/
│   ├── app/
│   └── package.json
│
├── knowledge/
│   ├── faq.md
│   ├── returns.md
│   ├── shipping.md
│   └── warranty.md
│
├── .env.example
└── .gitignore
```

## Getting Started

### Prerequisites

* Python 3.10+
* Node.js 18+
* An OpenAI API key

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd novashop-agent
```

### 2. Configure the API Key

Create a `.env` file in the `backend` directory:

```text
OPENAI_API_KEY=your_api_key_here
```

The API key is only used by the backend and is not exposed to the frontend.

### 3. Start the Backend

From the `backend` directory:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend will be available at:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/health
```

### 4. Start the Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

## AI Tools Used During Development

I used **Cursor** as an AI coding assistant throughout the development process.

I primarily used it to:

* Generate the initial project structure
* Implement the FastAPI and Next.js integration
* Develop the RAG pipeline
* Implement OpenAI tool calling
* Add streaming responses
* Add error handling
* Review and test implementation paths
* Iterate on the frontend UX

The most useful aspect was accelerating implementation while keeping the architecture intentionally small.

I still made the key product and architecture decisions manually, including:

* Choosing the e-commerce support use case
* Separating RAG from tools
* Selecting the minimum set of agent actions
* Choosing mock data instead of introducing production infrastructure
* Defining the agent's boundaries and escalation behavior

## Trade-offs

This project is intentionally designed as a prototype.

### In-Memory Vector Store

A production system would likely use a persistent vector database. For this assignment, an in-memory store keeps setup simple and makes the project easy to run locally.

### Mock Business Data

Orders, inventory, and tickets are stored in memory rather than connected to real business systems.

This demonstrates the agentic interaction pattern without requiring external services.

### Client-Side Conversation State

Conversation history is maintained in the browser rather than persisted in a database.

This is sufficient for a single-session prototype but would need to change for a production system.

### Limited Tool Set

I intentionally implemented three high-value actions rather than adding many tools. This keeps the agent behavior predictable and makes the user journey easier to demonstrate.

## What I Would Build Next

If this were developed into a real product, my next three features would be:

### 1. Persistent Customer Context

Store conversations and customer context so the agent can continue helping customers across sessions and channels.

### 2. Business Admin Interface

Allow a business owner to manage:

* Agent instructions
* Knowledge Base documents
* Business policies
* Available tools

without modifying code.

### 3. Support Analytics

Track conversations and agent behavior to help businesses understand:

* Most common support topics
* Unresolved questions
* Handoff rate
* Tool usage
* Customer-support trends

## Project Status

This project is a functional prototype demonstrating an end-to-end AI customer support experience:

**Chat UI → Agent → Knowledge Retrieval / Tools → Response**

It intentionally prioritizes a realistic user experience, clear agent boundaries, and simple architecture over production infrastructure.
