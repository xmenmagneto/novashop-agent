"use client";

export default function Home() {
  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>NovaShop</h1>
      <p>Customer Support AI Agent</p>
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          const form = e.currentTarget;
          const input = form.elements.namedItem("message") as HTMLInputElement;
          const message = input.value;
          if (!message.trim()) return;

          const output = document.getElementById("response");
          if (output) output.textContent = "Thinking...";

          try {
            const res = await fetch("http://localhost:8000/chat", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ message }),
            });
            const data = await res.json();
            if (output) output.textContent = data.response ?? "(empty response)";
          } catch (err) {
            if (output) output.textContent = "Error: " + err;
          }
        }}
      >
        <input
          type="text"
          name="message"
          placeholder="Type your message..."
          style={{ width: "300px", padding: "0.5rem" }}
        />
        <button type="submit" style={{ padding: "0.5rem 1rem", marginLeft: "0.5rem" }}>
          Send
        </button>
      </form>
      <div id="response" style={{ marginTop: "1rem", whiteSpace: "pre-wrap" }} />
    </main>
  );
}
