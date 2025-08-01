"use client";

import React, { useState, useRef, useEffect } from "react";
import styles from "../HomePage.module.css";

const ayurvedaGreeting = [
  "🌿 Welcome to Ayurveda Chatbot 🌿",
  "Ask me about natural remedies, herbs, and holistic health!",
];

type Result = {
  content: string;
  metadata: {
    source: string;
    page: number;
  };
  score: number;
};

type Message =
  | { from: "bot"; text: string; results?: Result[] }
  | { from: "user"; text: string };

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { from: "bot", text: ayurvedaGreeting[0] },
    { from: "bot", text: ayurvedaGreeting[1] },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showMeta, setShowMeta] = useState<{ [key: string]: boolean }>({});
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMessage: Message = { from: "user", text: input };
    setMessages((msgs) => [...msgs, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const url = 'http://localhost:8000/search';
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: input,
          k: 3,
          generate_response: true
        })
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      if (data?.results && Array.isArray(data.results) && data.results.length > 0) {
        const sortedResults = [...data.results].sort((a, b) => b.score - a.score);
        const topResult = sortedResults[0];
        setMessages((msgs) => [
          ...msgs,
          {
            from: "bot",
            text: data.generated_response?.text || "",
            results: [topResult],
          },
        ]);
      } else {
        setMessages((msgs) => [
          ...msgs,
          {
            from: "bot",
            text: "🌱 (No results found)",
          },
        ]);
      }
    } catch {
      setMessages((msgs) => [
        ...msgs,
        {
          from: "bot",
          text: "⚠️ Sorry, there was a problem connecting to the Ayurveda API.",
        },
      ]);
    }
    setLoading(false);
  };

  const handleShowMeta = (msgIdx: number, resIdx: number) => {
    setShowMeta((prev) => ({ ...prev, [`${msgIdx}-${resIdx}`]: !prev[`${msgIdx}-${resIdx}`] }));
  };

  return (
    <div className={styles.ayurvedaBg}>
      <div className={styles.centerBox}>
        <h1 className={styles.title}>Ayurveda Chatbot</h1>
        <div className={styles.chatWindow}>
          {messages.map((msg, msgIdx) =>
            msg.from === "bot" && msg.results ? (
              msg.results.map((res, resIdx) => (
                <div key={resIdx} className={styles.botMsg}>
                  <div>{res.content}</div>
                  <button
                    className={styles.metaBtn}
                    onClick={() => handleShowMeta(msgIdx, resIdx)}
                    type="button"
                  >
                    {showMeta[`${msgIdx}-${resIdx}`] ? "Hide Source" : "Show Source"}
                  </button>
                  {showMeta[`${msgIdx}-${resIdx}`] && (
                    <div className={styles.metaInfo}>
                      <span>Source: {res.metadata.source}</span>
                      <span>Page: {res.metadata.page}</span>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div
                key={msgIdx}
                className={msg.from === "user" ? styles.userMsg : styles.botMsg}
              >
                {msg.text}
              </div>
            )
          )}
          {loading && (
            <div className={styles.botMsg}>
              <span className={styles.loader}></span>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        <form className={styles.inputBar} onSubmit={handleSend}>
          <input
            className={styles.input}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your Ayurveda question..."
            disabled={loading}
          />
          <button className={styles.sendBtn} type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
