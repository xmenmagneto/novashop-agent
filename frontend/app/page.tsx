"use client";

import { useEffect, useRef, useState } from "react";

type Role = "user" | "assistant";

interface ChatMessage {
  role: Role;
  content: string;
  sources?: string[];
}

const BACKEND_URL = "http://localhost:8000";
const STREAM_URL = `${BACKEND_URL}/chat/stream`;

const EXAMPLE_QUESTIONS = [
  "Where is my order NS-10234?",
  "Is the Nova 4K Monitor available?",
  "What is your return policy?",
];

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the latest message whenever messages change.
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-grow the textarea up to a max height.
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
  }, [input]);

  const handleSend = async (text?: string) => {
    const messageText = (text ?? input).trim();
    if (!messageText || loading) return;

    setError(null);
    const userMessage: ChatMessage = { role: "user", content: messageText };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);

    // Add a placeholder assistant bubble that we'll stream into.
    const assistantIndex = nextMessages.length;
    setMessages([...nextMessages, { role: "assistant", content: "" }]);

    try {
      const res = await fetch(STREAM_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: nextMessages }),
      });

      if (!res.ok || !res.body) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data?.detail || `Request failed (${res.status})`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let accumulated = "";
      let sources: string[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? ""; // keep incomplete line for the next read

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const obj = JSON.parse(line);
            if (obj.type === "content") {
              accumulated += obj.text ?? "";
              // Update the assistant bubble in place (streaming).
              setMessages((prev) => {
                const copy = [...prev];
                if (copy[assistantIndex]) {
                  copy[assistantIndex] = { ...copy[assistantIndex], content: accumulated };
                }
                return copy;
              });
            } else if (obj.type === "sources") {
              sources = Array.isArray(obj.sources) ? obj.sources : [];
            } else if (obj.type === "error") {
              throw new Error(obj.message || "Something went wrong.");
            }
          } catch (e) {
            // Ignore malformed lines; only throw if it's an explicit error event.
            if (e instanceof Error && e.message) {
              // re-check: was this an error event?
            }
          }
        }
      }

      // Finalize: attach sources if any.
      setMessages((prev) => {
        const copy = [...prev];
        if (copy[assistantIndex]) {
          copy[assistantIndex] = { ...copy[assistantIndex], content: accumulated, sources };
        }
        return copy;
      });

      if (!accumulated) {
        throw new Error("Received an empty response.");
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong.";
      setError(msg);
      // Remove the empty placeholder assistant bubble if streaming failed early.
      setMessages((prev) => {
        const copy = [...prev];
        const last = copy[assistantIndex];
        if (last && last.role === "assistant" && !last.content) {
          copy.pop();
        } else if (last && last.role === "assistant") {
          // Keep whatever partial text streamed, but mark sources empty.
          copy[assistantIndex] = { ...last, sources: [] };
        }
        return copy;
      });
    } finally {
      setLoading(false);
      textareaRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter sends; Shift+Enter inserts a newline.
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <main style={styles.container}>
      <header style={styles.header}>
        <div style={styles.logo}>★</div>
        <div>
          <h1 style={styles.title}>NovaShop</h1>
          <p style={styles.subtitle}>Nova — Customer Support Agent</p>
        </div>
      </header>

      <div ref={scrollRef} style={styles.messages}>
        {messages.length === 0 && (
          <div style={styles.welcome}>
            <div style={styles.welcomeAvatar}>★</div>
            <h2 style={styles.welcomeTitle}>Hi, I&apos;m Nova</h2>
            <p style={styles.welcomeText}>
              Your NovaShop customer support assistant. Ask me about orders,
              products, shipping, returns, or anything else.
            </p>
            <div style={styles.examples}>
              {EXAMPLE_QUESTIONS.map((q) => (
                <button
                  key={q}
                  style={styles.exampleChip}
                  onClick={() => handleSend(q)}
                  disabled={loading}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            style={
              m.role === "user"
                ? { ...styles.row, ...styles.userRow }
                : { ...styles.row, ...styles.assistantRow }
            }
          >
            {m.role === "assistant" && <div style={styles.avatar}>★</div>}
            <div
              style={
                m.role === "user"
                  ? { ...styles.bubble, ...styles.userBubble }
                  : { ...styles.bubble, ...styles.assistantBubble }
              }
            >
              {m.role === "assistant" && (
                <div style={styles.bubbleRole}>Nova</div>
              )}
              <p style={styles.bubbleContent}>
                {m.content || <span style={styles.thinking}>Nova is thinking…</span>}
              </p>
              {m.role === "assistant" && m.sources && m.sources.length > 0 && (
                <div style={styles.sources}>
                  <span style={styles.sourcesLabel}>Sources:</span>{" "}
                  {m.sources.join(", ")}
                </div>
              )}
            </div>
          </div>
        ))}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div style={styles.error} role="alert">
          {error}
        </div>
      )}

      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        style={styles.form}
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message... (Enter to send, Shift+Enter for newline)"
          disabled={loading}
          rows={1}
          style={styles.textarea}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            ...styles.button,
            ...(loading || !input.trim() ? styles.buttonDisabled : {}),
          }}
        >
          {loading ? "…" : "Send"}
        </button>
      </form>
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    maxWidth: "760px",
    margin: "0 auto",
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif",
    boxSizing: "border-box",
    padding: "1rem",
    backgroundColor: "#fafafa",
  },
  header: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    borderBottom: "1px solid #e5e7eb",
    paddingBottom: "0.75rem",
    marginBottom: "1rem",
  },
  logo: {
    width: "36px",
    height: "36px",
    borderRadius: "50%",
    backgroundColor: "#2563eb",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "1.1rem",
  },
  title: { margin: 0, fontSize: "1.25rem", color: "#111827" },
  subtitle: { margin: "0.1rem 0 0", fontSize: "0.8rem", color: "#6b7280" },

  messages: {
    flex: 1,
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: "0.75rem",
    padding: "0.25rem 0.25rem 0.5rem",
  },

  welcome: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    textAlign: "center",
    padding: "2.5rem 1rem",
  },
  welcomeAvatar: {
    width: "56px",
    height: "56px",
    borderRadius: "50%",
    backgroundColor: "#2563eb",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "1.5rem",
    marginBottom: "1rem",
  },
  welcomeTitle: { margin: "0 0 0.5rem", fontSize: "1.3rem", color: "#111827" },
  welcomeText: { margin: "0 0 1.5rem", color: "#6b7280", maxWidth: "420px" },
  examples: {
    display: "flex",
    flexWrap: "wrap",
    gap: "0.5rem",
    justifyContent: "center",
  },
  exampleChip: {
    padding: "0.5rem 0.85rem",
    border: "1px solid #d1d5db",
    backgroundColor: "#fff",
    borderRadius: "999px",
    fontSize: "0.82rem",
    color: "#374151",
    cursor: "pointer",
  },

  row: {
    display: "flex",
    gap: "0.5rem",
    maxWidth: "100%",
  },
  userRow: {
    justifyContent: "flex-end",
  },
  assistantRow: {
    justifyContent: "flex-start",
  },
  avatar: {
    width: "28px",
    height: "28px",
    borderRadius: "50%",
    backgroundColor: "#2563eb",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "0.8rem",
    flexShrink: 0,
    marginTop: "0.2rem",
  },

  bubble: {
    maxWidth: "80%",
    padding: "0.6rem 0.9rem",
    borderRadius: "14px",
    lineHeight: 1.5,
    wordBreak: "break-word",
    whiteSpace: "pre-wrap",
  },
  userBubble: {
    backgroundColor: "#2563eb",
    color: "#fff",
    borderBottomRightRadius: "4px",
  },
  assistantBubble: {
    backgroundColor: "#fff",
    color: "#111827",
    border: "1px solid #e5e7eb",
    borderBottomLeftRadius: "4px",
  },
  bubbleRole: {
    fontSize: "0.72rem",
    color: "#2563eb",
    fontWeight: 600,
    marginBottom: "0.2rem",
  },
  bubbleContent: {
    margin: 0,
    fontSize: "0.95rem",
  },
  thinking: {
    color: "#9ca3af",
    fontStyle: "italic",
  },
  sources: {
    marginTop: "0.5rem",
    fontSize: "0.72rem",
    color: "#6b7280",
    fontStyle: "italic",
  },
  sourcesLabel: {
    fontWeight: 600,
  },

  error: {
    backgroundColor: "#fee2e2",
    color: "#991b1b",
    padding: "0.6rem 0.85rem",
    borderRadius: "8px",
    marginBottom: "0.75rem",
    fontSize: "0.85rem",
  },

  form: {
    display: "flex",
    gap: "0.5rem",
    borderTop: "1px solid #e5e7eb",
    paddingTop: "0.75rem",
    alignItems: "flex-end",
  },
  textarea: {
    flex: 1,
    padding: "0.6rem 0.75rem",
    border: "1px solid #d1d5db",
    borderRadius: "10px",
    fontSize: "0.95rem",
    outline: "none",
    resize: "none",
    fontFamily: "inherit",
    lineHeight: 1.4,
    maxHeight: "140px",
    overflowY: "auto",
  },
  button: {
    padding: "0.6rem 1.4rem",
    backgroundColor: "#2563eb",
    color: "#fff",
    border: "none",
    borderRadius: "10px",
    fontSize: "0.95rem",
    cursor: "pointer",
    minWidth: "70px",
  },
  buttonDisabled: {
    backgroundColor: "#9ca3af",
    cursor: "not-allowed",
  },
};
