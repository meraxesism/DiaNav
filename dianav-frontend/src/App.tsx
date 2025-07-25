import React, { useRef, useState, useEffect } from 'react';
import './App.css';

interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
}
interface ChatSession {
  id: string;
  heading: string;
  messages: ChatMessage[];
}

const exampleQuestions = [
  'What causes B1087?',
  'How do I troubleshoot LIN bus off error?',
  'Tell me all symptoms for B1087.',
  'What is a DTC code?',
];

function App() {
  const [chats, setChats] = useState<ChatSession[]>([{
    id: '1',
    heading: 'New Chat',
    messages: [],
  }]);
  const [activeChatId, setActiveChatId] = useState('1');
  const [input, setInput] = useState('');
  const [showWelcome, setShowWelcome] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const [welcomeHeight, setWelcomeHeight] = useState(0);
  const welcomeRef = useRef<HTMLDivElement | null>(null);

  const activeChat = chats.find(c => c.id === activeChatId)!;

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    if (activeChat.messages.length > 0 && showWelcome) {
      setTimeout(() => setShowWelcome(false), 350); // allow animation
    }
    // eslint-disable-next-line
  }, [activeChat.messages, showWelcome]);

  useEffect(() => {
    if (showWelcome && welcomeRef.current) {
      setWelcomeHeight(welcomeRef.current.offsetHeight);
    } else {
      setWelcomeHeight(0);
    }
  }, [showWelcome]);

  const handleSend = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;
    const userMsg: ChatMessage = { sender: 'user', text: input };
    const updatedChats = chats.map(chat =>
      chat.id === activeChatId
        ? { ...chat, messages: [...chat.messages, userMsg] }
        : chat
    );
    setChats(updatedChats);
    setInput('');
    // Simulate AI response
    setTimeout(() => {
      setChats(chats => chats.map(chat =>
        chat.id === activeChatId
          ? { ...chat, messages: [...chat.messages, { sender: 'ai', text: `You said: "${userMsg.text}" (replace with real AI response)` }] }
          : chat
      ));
    }, 800);
    // Set heading if it's still 'New Chat'
    if (activeChat.heading === 'New Chat') {
      setChats(chats => chats.map(chat =>
        chat.id === activeChatId
          ? { ...chat, heading: userMsg.text.slice(0, 30) + (userMsg.text.length > 30 ? '...' : '') }
          : chat
      ));
    }
    if (showWelcome) setShowWelcome(false);
  };

  const handleExampleClick = (q: string) => {
    setInput(q);
    setTimeout(() => handleSend(), 100);
  };

  const handleNewChat = () => {
    const newId = (Date.now() + Math.random()).toString();
    setChats([{ id: newId, heading: 'New Chat', messages: [] }, ...chats]);
    setActiveChatId(newId);
    setInput('');
    setShowWelcome(true);
  };

  return (
    <div className={`dianav-app-wide${sidebarOpen ? '' : ' sidebar-collapsed'}`}>
      <aside className={`dianav-sidebar${sidebarOpen ? '' : ' collapsed'}`}>
        <div className="dianav-sidebar-toggle-row">
          <button className="dianav-sidebar-toggle" onClick={() => setSidebarOpen(v => !v)}>
            {sidebarOpen ? '<' : '>'}
          </button>
        </div>
        {sidebarOpen && <>
          <button className="dianav-newchat-btn" onClick={handleNewChat}>+ New Chat</button>
          <div className="dianav-chat-list">
            {chats.map(chat => (
              <div
                key={chat.id}
                className={`dianav-chat-heading${chat.id === activeChatId ? ' active' : ''}`}
                onClick={() => { setActiveChatId(chat.id); setShowWelcome(chat.messages.length === 0); }}
              >
                {chat.heading}
              </div>
            ))}
          </div>
        </>}
      </aside>
      <div className={`dianav-center-wrap${sidebarOpen ? '' : ' center-absolute'}`}>
        <div className="dianav-root dianav-root-wide">
          <header className="dianav-header">
            <div className="dianav-logo">
              {/* Tata logo placeholder, replace later */}
              <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="18" cy="18" r="18" fill="#fff" />
                <text x="18" y="24" textAnchor="middle" fontSize="18" fill="#184077" fontFamily="Arial" fontWeight="bold">T</text>
              </svg>
            </div>
            <div className="dianav-title">DIAGNOSTIC NAVIGATOR</div>
            <div className="dianav-ai-label">AI Assistant</div>
          </header>
          <main className="dianav-main">
            <div
              className={`dianav-welcome${showWelcome ? ' show' : ' hide'}`}
              ref={welcomeRef}
              style={{ pointerEvents: showWelcome ? 'auto' : 'none' }}
            >
              <h1 className="dianav-h1">Hello! I'm your Diagnostic Assistant.</h1>
              <div className="dianav-subtitle">How can I help you today?</div>
              <div className="dianav-example-questions">
                {exampleQuestions.map((q, i) => (
                  <button key={i} className="dianav-example-btn" onClick={() => handleExampleClick(q)}>
                    {q}
                  </button>
                ))}
              </div>
            </div>
            <div
              className="dianav-welcome-placeholder"
              style={{ height: showWelcome ? welcomeHeight : 0 }}
            />
            <div className="dianav-chat-card">
              <div className="dianav-chat-window">
                {activeChat.messages.map((msg, i) => (
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
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
