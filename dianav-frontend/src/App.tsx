import React, { useRef, useState, useEffect } from 'react';
import './App.css';

interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  images?: DiagnosticImage[];
  structured?: string;
}

interface DiagnosticImage {
  image_data: string;
  description: string;
  page_num: number;
}

interface ChatSession {
  id: string;
  heading: string;
  messages: ChatMessage[];
}

interface ApiResponse {
  conversational: string;
  structured: string;
  images: DiagnosticImage[];
  has_images: boolean;
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
  const [isLoading, setIsLoading] = useState(false);
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

  const sendMessageToBackend = async (message: string): Promise<ApiResponse> => {
    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: message }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error sending message to backend:', error);
      return {
        conversational: "I'm sorry, I'm having trouble connecting to the diagnostic system. Please try again later.",
        structured: "Connection error",
        images: [],
        has_images: false
      };
    }
  };

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    const userMsg: ChatMessage = { sender: 'user', text: input };
    const updatedChats = chats.map(chat =>
      chat.id === activeChatId
        ? { ...chat, messages: [...chat.messages, userMsg] }
        : chat
    );
    setChats(updatedChats);
    setInput('');
    setIsLoading(true);
    
    try {
      const response = await sendMessageToBackend(input);
      const aiMsg: ChatMessage = {
        sender: 'ai',
        text: response.conversational,
        structured: response.structured,
        images: response.images
      };
      
      setChats(chats => chats.map(chat =>
        chat.id === activeChatId
          ? { ...chat, messages: [...chat.messages, aiMsg] }
          : chat
      ));
    } catch (error) {
      console.error('Error in handleSend:', error);
      const errorMsg: ChatMessage = {
        sender: 'ai',
        text: "I'm sorry, I encountered an error while processing your request. Please try again."
      };
      
      setChats(chats => chats.map(chat =>
        chat.id === activeChatId
          ? { ...chat, messages: [...chat.messages, errorMsg] }
          : chat
      ));
    } finally {
      setIsLoading(false);
    }
    
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
    setChats(prevChats => [{ id: newId, heading: 'New Chat', messages: [] }, ...prevChats]);
    setActiveChatId(newId);
    setInput('');
    setShowWelcome(true);
  };

  const renderMessage = (msg: ChatMessage, index: number) => (
    <div key={index} className={`dianav-chat-bubble ${msg.sender}`}>
      <div className="dianav-message-text">{msg.text}</div>
      
      {msg.structured && (
        <div className="dianav-structured-data">
          <details>
            <summary>View Diagnostic Details</summary>
            <pre>{msg.structured}</pre>
          </details>
        </div>
      )}
      
      {msg.images && msg.images.length > 0 && (
        <div className="dianav-images-container">
          <h4>Diagnostic Images:</h4>
          {msg.images.map((img, imgIndex) => (
            <div key={imgIndex} className="dianav-image-item">
              <img 
                src={img.image_data} 
                alt={img.description}
                className="dianav-diagnostic-image"
                loading="lazy"
              />
              <p className="dianav-image-description">
                {img.description} (Page {img.page_num + 1})
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className={`dianav-app-wide${sidebarOpen ? '' : ' sidebar-collapsed'}`}>
      <aside className={`dianav-sidebar${sidebarOpen ? '' : ' collapsed'}`}>
        <div className="dianav-sidebar-toggle-row">
          <button className="dianav-sidebar-toggle" onClick={() => setSidebarOpen(v => !v)}>
            {sidebarOpen ? '<' : '>'}
          </button>
        </div>
        <div className="dianav-newchat-row">
          {sidebarOpen ? (
            <button className="dianav-newchat-btn" onClick={handleNewChat}>+ New Chat</button>
          ) : (
            <button className="dianav-newchat-btn-collapsed" title="New Chat" onClick={handleNewChat}>+</button>
          )}
        </div>
        {sidebarOpen && (
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
        )}
      </aside>
      <div className={`dianav-center-wrap${sidebarOpen ? '' : ' center-absolute'}`}>
        <div className="dianav-root dianav-root-wide">
          <header className="dianav-header">
            <div className="dianav-logo">
              <img src="/tata-logo.png" alt="Tata Motors Logo" style={{ width: 48, height: 48, objectFit: 'contain' }} />
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
                {activeChat.messages.map((msg, i) => renderMessage(msg, i))}
                {isLoading && (
                  <div className="dianav-chat-bubble ai">
                    <div className="dianav-loading">
                      <div className="dianav-loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                      <p>Processing your diagnostic query...</p>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>
              <form className="dianav-input-row" onSubmit={handleSend} autoComplete="off">
                <input
                  type="text"
                  placeholder="Enter your message"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  disabled={isLoading}
                  autoFocus
                />
                <button type="submit" disabled={isLoading}>
                  {isLoading ? 'Sending...' : 'Send'}
                </button>
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
