"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface Props {
  context: string;
  onClose: () => void;
}

export default function DeepDiveChat({ context, onClose }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasInitRef = useRef(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-trigger initial analysis
  useEffect(() => {
    if (!hasInitRef.current && context) {
      hasInitRef.current = true;
      sendMessage("Provide a detailed analysis of this topic.");
    }
  }, [context]);

  async function sendMessage(question: string) {
    if (!question.trim() || loading) return;

    const userMsg: Message = { role: "user", content: question };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const history = messages.map((m) => ({
        role: m.role === "user" ? "user" : "model",
        parts: [{ text: m.content }],
      }));

      const res = await fetch("/api/deep-dive", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ context, question, history }),
      });

      if (!res.ok) throw new Error("Request failed");

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let assistantContent = "";

      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        assistantContent += decoder.decode(value);
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: "assistant", content: assistantContent };
          return updated;
        });
      }
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Analysis unavailable. Check that GEMINI_API_KEY is configured." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div className="relative w-full max-w-lg bg-[var(--bg-primary)] h-full flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[var(--border)]">
          <h2 className="text-sm font-semibold">Deep Dive Analysis</h2>
          <button
            onClick={onClose}
            className="text-[var(--text-muted)] hover:text-[var(--text-primary)] text-lg"
          >
            ✕
          </button>
        </div>

        {/* Context */}
        <div className="px-4 py-3 bg-[var(--bg-secondary)] border-b border-[var(--border)]">
          <p className="text-xs text-[var(--text-muted)] line-clamp-2">{context}</p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={msg.role === "user" ? "text-right" : ""}>
              {msg.role === "user" ? (
                <span className="inline-block bg-[var(--text-primary)] text-[var(--bg-primary)] text-sm rounded-lg px-3 py-2 max-w-[80%]">
                  {msg.content}
                </span>
              ) : (
                <div className="text-sm text-[var(--text-secondary)] leading-relaxed whitespace-pre-wrap">
                  {msg.content}
                  {loading && i === messages.length - 1 && (
                    <span className="inline-block w-1.5 h-4 bg-[var(--text-muted)] ml-0.5 animate-pulse" />
                  )}
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-[var(--border)]">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              sendMessage(input);
            }}
            className="flex gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a follow-up question..."
              disabled={loading}
              className="flex-1 px-3 py-2 text-sm rounded-lg border border-[var(--border)] bg-[var(--bg-primary)] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-1 focus:ring-[var(--text-muted)] disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-4 py-2 text-sm font-medium bg-[var(--text-primary)] text-[var(--bg-primary)] rounded-lg disabled:opacity-30"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
