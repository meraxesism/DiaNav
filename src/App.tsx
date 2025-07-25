import React, { useRef, useState, useEffect } from 'react';
import './App.css';

interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg: ChatMessage = { sender: 'user', text: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput('');
    // Simulate AI response
    setTimeout(() => {
      setMessages((msgs) => [
        ...msgs,
        { sender: 'ai', text: `You said: "${userMsg.text}" (replace with real AI response)` },
      ]);
    }, 800);
  };

  return (
    <div className="dianav-outer">
      <div className="dianav-root">
        <header className="dianav-header">
          <div className="dianav-logo">
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="18" cy="18" r="18" fill="#fff" />
              <rect x="8" y="16" width="20" height="4" rx="2" fill="#1A3A6B" />
            </svg>
          </div>
          <div className="dianav-title">DIAGNOSTIC NAVIGATOR</div>
          <div className="dianav-ai-label">AI Assistant</div>
        </header>
        <main className="dianav-main">
          <h1 className="dianav-h1">Hello! I'm your Diagnostic Assistant.</h1>
          <div className="dianav-subtitle">How can I help you today?</div>
          <div className="dianav-chat-window">
            {messages.map((msg, i) => (
              <div key={i} className={`dianav-chat-bubble ${msg.sender}`}>{msg.text}</div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <form className="dianav-input-row" onSubmit={handleSend} autoComplete="off">
            <input
              type="text"
              placeholder="Enter your message"
              value={input}
              onChange={e => setInput(e.target.value)}
              autoFocus
            />
            <button type="submit">Send</button>
          </form>
          <footer className="dianav-footer">Powered by Tata Motors</footer>
        </main>
      </div>
    </div>
  );
}

export default App; 