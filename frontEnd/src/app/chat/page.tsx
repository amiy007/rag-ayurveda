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
      const params = new URLSearchParams({
        query: input,
        k: '3',
        generate_response: 'true',
        model: 'gemini' // Using gemini as the default model as per user's example
      });
      
      const url = `http://localhost:8000/search?${params.toString()}`;
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
        },
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      
      // Sort results by score in descending order
      const sortedResults = data?.results && Array.isArray(data.results)
        ? [...data.results].sort((a, b) => b.score - a.score)
        : [];
      
      // Get the generated response or use a default message
      const responseText = data.generated_response?.response || 
        (sortedResults.length > 0 
          ? "Here's what I found in the Ayurvedic knowledge base:"
          : "I couldn't find specific information about this in the knowledge base. Could you try rephrasing your question?");
      
      setMessages((msgs) => [
        ...msgs,
        {
          from: "bot",
          text: responseText,
          results: sortedResults.slice(0, 3), // Show top 3 results
        },
      ]);
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
          {messages.map((msg, msgIdx) => {
            if (msg.from === "bot" && msg.results && msg.results.length > 0) {
              return (
                <div key={msgIdx} className={styles.botMsg}>
                  {/* LLM Response */}
                  <div className={styles.botText}>
                    {msg.text}
                  </div>
                  
                  {/* Search Results */}
                  <div className={styles.searchResults}>
                    <div className={styles.resultsHeader}>Relevant Information:</div>
                    {msg.results.map((res, resIdx) => (
                      <div key={resIdx} className={styles.resultItem}>
                        <div className={styles.resultContent}>
                          {res.content.split('\n').map((paragraph, pIdx) => (
                            <p key={pIdx} className={styles.resultParagraph}>
                              {paragraph}
                            </p>
                          ))}
                        </div>
                        <button
                          className={styles.metaBtn}
                          onClick={() => handleShowMeta(msgIdx, resIdx)}
                          type="button"
                        >
                          {showMeta[`${msgIdx}-${resIdx}`] ? "Hide Source" : "Show Source"}
                        </button>
                        {showMeta[`${msgIdx}-${resIdx}`] && (
                          <div className={styles.metaInfo}>
                            <div><strong>Source:</strong> {res.metadata.source}</div>
                            <div><strong>Page:</strong> {res.metadata.page}</div>
                            <div><strong>Relevance Score:</strong> {res.score.toFixed(2)}</div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              );
            }
            
            // Regular message (user or bot without results)
            return (
              <div
                key={msgIdx}
                className={msg.from === "user" ? styles.userMsg : styles.botMsg}
              >
                {msg.text}
              </div>
            );
          })}
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
