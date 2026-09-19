"use client";

import { useEffect, useRef, useState } from "react";

type Role = "user" | "assistant";

interface ChatMessage {
  role: Role;
  content: string;
}

const BACKEND_URL = "http://localhost:8000/chat";

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to the latest message whenever messages change.
  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    // Clear any previous error and add the user's message immediately.
    setError(null);
    const nextMessages: ChatMessage[] = [...messages, { role: "user", content: trimmed }];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(BACKEND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: nextMessages }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data?.detail || `Request failed (${res.status})`);
      }

      const reply: string = data.response ?? "(empty response)";
      setMessages([...nextMessages, { role: "assistant", content: reply }]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong.";
      setError(msg);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <main style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>NovaShop</h1>
        <p style={styles.subtitle}>Nova — Customer Support Agent</p>
      </header>

      <div ref={scrollRef} style={styles.messages}>
        {messages.length === 0 && (
          <p style={styles.empty}>
            Hi, I&apos;m Nova. How can I help you today?
          </p>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            style={
              m.role === "user"
                ? { ...styles.bubble, ...styles.userBubble }
                : { ...styles.bubble, ...styles.assistantBubble }
            }
          >
            <strong style={styles.bubbleRole}>
              {m.role === "user" ? "You" : "Nova"}
            </strong>
            <p style={styles.bubbleContent}>{m.content}</p>
          </div>
        ))}

        {loading && (
          <div style={{ ...styles.bubble, ...styles.assistantBubble }}>
            <strong style={styles.bubbleRole}>Nova</strong>
            <p style={styles.bubbleContent}>Thinking…</p>
          </div>
        )}
      </div>

      {error && (
        <div style={styles.error}>
          Sorry, something went wrong: {error}
        </div>
      )}

      <form onSubmit={handleSend} style={styles.form}>
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
          style={styles.input}
        />
        <button type="submit" disabled={loading || !input.trim()} style={styles.button}>
          {loading ? "Sending…" : "Send"}
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
    maxWidth: "720px",
    margin: "0 auto",
    fontFamily: "system-ui, -apple-system, sans-serif",
    boxSizing: "border-box",
    padding: "1rem",
  },
  header: {
    borderBottom: "1px solid #e5e7eb",
    paddingBottom: "0.75rem",
    marginBottom: "1rem",
  },
  title: { margin: 0, fontSize: "1.5rem", color: "#111827" },
  subtitle: { margin: "0.25rem 0 0", fontSize: "0.9rem", color: "#6b7280" },
  messages: {
    flex: 1,
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: "0.75rem",
    paddingRight: "0.25rem",
  },
  empty: { color: "#9ca3af", fontStyle: "italic" },
  bubble: {
    maxWidth: "80%",
    padding: "0.6rem 0.9rem",
    borderRadius: "12px",
    lineHeight: 1.4,
    wordBreak: "break-word",
  },
  userBubble: {
    alignSelf: "flex-end",
    backgroundColor: "#2563eb",
    color: "#fff",
  },
  assistantBubble: {
    alignSelf: "flex-start",
    backgroundColor: "#f3f4f6",
    color: "#111827",
  },
  bubbleRole: { fontSize: "0.75rem", opacity: 0.8, display: "block" },
  bubbleContent: { margin: "0.25rem 0 0" },
  error: {
    backgroundColor: "#fee2e2",
    color: "#991b1b",
    padding: "0.5rem 0.75rem",
    borderRadius: "8px",
    marginBottom: "0.75rem",
    fontSize: "0.85rem",
  },
  form: {
    display: "flex",
    gap: "0.5rem",
    borderTop: "1px solid #e5e7eb",
    paddingTop: "0.75rem",
  },
  input: {
    flex: 1,
    padding: "0.6rem 0.75rem",
    border: "1px solid #d1d5db",
    borderRadius: "8px",
    fontSize: "0.95rem",
    outline: "none",
  },
  button: {
    padding: "0.6rem 1.25rem",
    backgroundColor: "#2563eb",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    fontSize: "0.95rem",
    cursor: "pointer",
  },
};
