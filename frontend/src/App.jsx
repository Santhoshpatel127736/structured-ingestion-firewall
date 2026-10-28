
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function sendMessage(e) {
    e.preventDefault();

    const text = message.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setMessage("");
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.error || "Request failed");
      }

      setSessionId(data.session_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response_markdown },
      ]);
    } catch (err) {
      setError(err.message || "Could not connect to the server.");
    } finally {
      setLoading(false);
    }
  }

  function newChat() {
    setSessionId(null);
    setMessages([]);
    setMessage("");
    setError("");
  }

  return (
    <main className="app">
      <header className="app-header">
        <div>
          <h1>AI Support Assistant</h1>
          <p>Enterprise Ingestion Firewall · Conversation Memory</p>
        </div>
        <button
          type="button"
          className="new-chat-button"
          onClick={newChat}
          disabled={loading}
        >
          + New Chat
        </button>
      </header>

      <section className="chat-window">
        {messages.length === 0 && (
          <div className="welcome">
            <h2>How can I help you today?</h2>
            <p>Ask a question to start a new conversation.</p>
          </div>
        )}

        {messages.map((item, index) => (
          <article className={`message ${item.role}`} key={index}>
            <strong>{item.role === "user" ? "You" : "AI Assistant"}</strong>
            <div className="message-content">
              <ReactMarkdown>{item.content}</ReactMarkdown>
            </div>
          </article>
        ))}

        {loading && (
          <article className="message assistant">
            <strong>AI Assistant</strong>
            <p>Thinking...</p>
          </article>
        )}

        {error && <p className="error-message">Error: {error}</p>}
      </section>

      <form className="chat-form" onSubmit={sendMessage}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          rows={2}
          maxLength={10000}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !message.trim()}>
          {loading ? "Sending..." : "Send"}
        </button>
      </form>
    </main>
  );
}

export default App;
