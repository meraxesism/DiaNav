import React, { useRef, useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Analytics } from '@vercel/analytics/react';
import { useTranslation } from 'react-i18next';
import i18n from './i18n';
import './App.css';
import LanguageSwitcher from './components/LanguageSwitcher';
import './components/LanguageSwitcher.css';

// Determine backend API base URL from environment with sensible fallback
const API_BASE: string = (() => {
  const envUrl = (process.env.REACT_APP_BACKEND_URL || '').trim();
  if (envUrl) {
    // remove any trailing slash
    return envUrl.replace(/\/+$/, '');
  }
  return 'http://localhost:8000';
})();

interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  images?: DiagnosticImage[];
  structured?: string;
  timestamp?: Date;
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
  createdAt: Date;
  lastModified: Date;
  vehicleInfo?: VehicleInfo;
}

interface VehicleInfo {
  make?: string;
  model?: string;
  year?: string;
  vin?: string;
}

interface ApiResponse {
  conversational: string;
  structured: string;
  images: DiagnosticImage[];
  has_images: boolean;
  search_method?: string;
  confidence?: string;
}

// Enhanced example questions with categories
const exampleQuestions = [
  { category: 'Common DTCs', questions: ['What causes B1087?', 'B155A-01 symptoms'], tKey: 'commonDTCs' },
  { category: 'Symptoms', questions: ['Seat movement problem', 'LIN bus communication error'], tKey: 'symptoms' },
  { category: 'Quick Search', questions: ['B108 (partial code)', 'Electrical fault'], tKey: 'quickSearch' },
];

// Quick actions for common diagnostic tasks
const quickActions = [
  { label: '🔍 Search DTC', action: 'search_dtc', description: 'Find diagnostic codes', tKey: 'searchDTC' },
  { label: '📊 System Check', action: 'system_check', description: 'Check vehicle systems', tKey: 'systemCheck' },
  { label: '🔧 Troubleshoot', action: 'troubleshoot', description: 'Step-by-step guidance', tKey: 'troubleshoot' },
  { label: '📋 Generate Report', action: 'generate_report', description: 'Create diagnostic report', tKey: 'generateReport' },
];

function App() {
  const { t } = useTranslation();
  const [chats, setChats] = useState<ChatSession[]>([{
    id: '1',
    heading: t('common.newChat'),
    messages: [],
    createdAt: new Date(),
    lastModified: new Date(),
  }]);
  const [activeChatId, setActiveChatId] = useState('');
  const [input, setInput] = useState('');
  const [showWelcome, setShowWelcome] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth > 768);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<DiagnosticImage | null>(null);
  const [showImageModal, setShowImageModal] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(window.innerWidth <= 768);
  const [searchFilter, setSearchFilter] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState<Array<{id: string, message: string, type: 'success' | 'error' | 'info'}>>([]);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const [welcomeHeight, setWelcomeHeight] = useState(0);
  const welcomeRef = useRef<HTMLDivElement | null>(null);
  const [chatWindowClass, setChatWindowClass] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  // Update chat headings when language changes
  useEffect(() => {
    const handleLanguageChange = () => {
      setChats(prevChats => 
        prevChats.map(chat => ({
          ...chat,
          heading: chat.heading === 'New Chat' ? t('common.newChat') : chat.heading
        }))
      );
    };

    window.addEventListener('languageChanged', handleLanguageChange);
    return () => window.removeEventListener('languageChanged', handleLanguageChange);
  }, [t]);

  const activeChat = chats.find(c => c.id === activeChatId) || {
    id: activeChatId,
    heading: 'New Chat',
    messages: [],
    createdAt: new Date(),
    lastModified: new Date()
  };
  


  // Add notification
  const addNotification = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Date.now().toString();
    setNotifications(prev => [...prev, { id, message, type }]);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 3000);
  };

  // Remove notification
  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  // Function to determine chat window expansion class
  const getChatWindowClass = (messages: ChatMessage[]) => {
    if (messages.length === 0) return '';
    
    const totalLength = messages.reduce((sum, msg) => sum + msg.text.length, 0);
    const messageCount = messages.length;
    
    // Very long conversations (many messages or very long content)
    if (messageCount >= 8 || totalLength >= 6000) {
      return 'very-expanded';
    }
    // Long conversations (moderate messages or long content)
    else if (messageCount >= 4 || totalLength >= 2000) {
      return 'expanded';
    }
    
    return '';
  };

      // Save chats to localStorage
    useEffect(() => {
      localStorage.setItem('dianav-chats', JSON.stringify(chats));
    }, [chats]);

  // Load chats from localStorage on startup
  useEffect(() => {
    const savedChats = localStorage.getItem('dianav-chats');
    if (savedChats) {
      try {
        const parsedChats = JSON.parse(savedChats);
        // Convert string dates back to Date objects
        const chatsWithDates = parsedChats.map((chat: any) => ({
          ...chat,
          createdAt: new Date(chat.createdAt),
          lastModified: new Date(chat.lastModified),
          messages: chat.messages.map((msg: any) => ({
            ...msg,
            timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date()
          }))
        }));
        setChats(chatsWithDates);
        // Set active chat to the first one if available
        if (chatsWithDates.length > 0 && !activeChatId) {
          setActiveChatId(chatsWithDates[0].id);
        }
      } catch (error) {
        console.error('Error loading saved chats:', error);
      }
    } else {
      // Create a default chat if no saved chats exist
      const defaultChatId = (Date.now() + Math.random()).toString();
      const defaultChat: ChatSession = {
        id: defaultChatId,
        heading: 'New Chat',
        messages: [],
        createdAt: new Date(),
        lastModified: new Date()
      };
      setChats([defaultChat]);
      setActiveChatId(defaultChatId);
    }
  }, []); // Empty dependency array - only run once on mount

  // Ensure we always have an active chat
  useEffect(() => {
    if (chats.length > 0 && !activeChatId) {
      setActiveChatId(chats[0].id);
    }
  }, [chats, activeChatId]);



  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    if (activeChat.messages.length > 0 && showWelcome) {
      setTimeout(() => setShowWelcome(false), 350); // allow animation
    }
    
    // Update chat window class based on conversation length
    setChatWindowClass(getChatWindowClass(activeChat.messages));
    // eslint-disable-next-line
  }, [activeChat.messages, showWelcome]);

  useEffect(() => {
    if (showWelcome && welcomeRef.current) {
      setWelcomeHeight(welcomeRef.current.offsetHeight);
    } else {
      setWelcomeHeight(0);
    }
  }, [showWelcome]);

  // Handle image click to open modal
  const handleImageClick = (image: DiagnosticImage) => {
    setSelectedImage(image);
    setShowImageModal(true);
  };

  // Close image modal
  const closeImageModal = () => {
    setShowImageModal(false);
    setSelectedImage(null);
  };

  // Handle escape key to close modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && showImageModal) {
        closeImageModal();
      }
    };

    if (showImageModal) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [showImageModal]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyboardShortcuts = (e: KeyboardEvent) => {
      // Ctrl/Cmd + N: New chat
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        handleNewChat();
      }
      
      // Ctrl/Cmd + K: Quick actions
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setShowQuickActions(!showQuickActions);
      }
      
      // Ctrl/Cmd + S: Export current chat
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        exportChat(activeChatId);
      }
      
      // Ctrl/Cmd + /: Show keyboard shortcuts help
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        showKeyboardShortcutsHelp();
      }
      
      // Ctrl/Cmd + B: Toggle sidebar
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        setSidebarOpen(v => !v);
      }
    };

    document.addEventListener('keydown', handleKeyboardShortcuts);
    return () => document.removeEventListener('keydown', handleKeyboardShortcuts);
  }, [activeChatId, showQuickActions]);

  // Mobile touch gestures and responsive behavior
  useEffect(() => {
    const handleResize = () => {
      const isMobile = window.innerWidth <= 768;
      if (isMobile && sidebarOpen) {
        setSidebarOpen(false);
      } else if (!isMobile && !sidebarOpen) {
        setSidebarOpen(true);
      }
      
      // Update Quick Actions visibility based on screen size
      setShowQuickActions(isMobile);
    };

    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
      // Add mobile-specific classes
      document.body.classList.add('mobile-device');
      
      // Touch gesture handling for sidebar
      let touchStartX = 0;
      let touchEndX = 0;
      
      const handleTouchStart = (e: TouchEvent) => {
        touchStartX = e.changedTouches[0].screenX;
      };
      
      const handleTouchEnd = (e: TouchEvent) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
      };
      
      const handleSwipe = () => {
        const swipeThreshold = 50;
        if (touchEndX < touchStartX - swipeThreshold) {
          // Swipe left - close sidebar
          setSidebarOpen(false);
        } else if (touchEndX > touchStartX + swipeThreshold) {
          // Swipe right - open sidebar
          setSidebarOpen(true);
        }
      };
      
      document.addEventListener('touchstart', handleTouchStart);
      document.addEventListener('touchend', handleTouchEnd);
      
      return () => {
        document.removeEventListener('touchstart', handleTouchStart);
        document.removeEventListener('touchend', handleTouchEnd);
        document.body.classList.remove('mobile-device');
      };
    }

    // Add resize listener
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [sidebarOpen]);

  // Handle mobile sidebar toggle
  const handleMobileSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Enhanced mobile sidebar handling
  const handleSidebarToggle = () => {
    if (window.innerWidth <= 768) {
      // Mobile: toggle sidebar with slide animation
      setSidebarOpen(!sidebarOpen);
    } else {
      // Desktop: use existing behavior
      setSidebarOpen(!sidebarOpen);
    }
  };

  // Show keyboard shortcuts help
  const showKeyboardShortcutsHelp = () => {
    const helpText = `Keyboard Shortcuts:
    
⌘/Ctrl + N: New Chat
⌘/Ctrl + K: Quick Actions
⌘/Ctrl + S: Export Chat
⌘/Ctrl + B: Toggle Sidebar
⌘/Ctrl + /: Show This Help
Escape: Close Modals

Navigation:
↑/↓: Navigate through chat history
Enter: Send message
Tab: Focus input field`;
    
    alert(helpText);
  };

  // Handle quick actions
  const handleQuickAction = (action: string) => {
    let userMessage = '';
    switch (action) {
      case 'search_dtc':
        userMessage = 'I need help finding diagnostic codes.';
        break;
      case 'system_check':
        userMessage = 'I want to check my vehicle systems.';
        break;
      case 'troubleshoot':
        userMessage = 'I need step-by-step troubleshooting guidance.';
        break;
      case 'generate_report':
        userMessage = 'I want to generate a diagnostic report.';
        break;
      case 'component_search':
        userMessage = 'I need help with a specific vehicle component.';
        break;
      case 'symptom_analysis':
        userMessage = 'I need to analyze symptoms I\'m experiencing.';
        break;
    }
    
    // Set the input with the user's request and send it
    setInput(userMessage);
    setShowQuickActions(false);
    
    // Send the message after a short delay to ensure input is set
    setTimeout(() => {
      handleSend();
    }, 100);
  };

  // Export chat session
  const exportChat = (chatId: string) => {
    const chat = chats.find(c => c.id === chatId);
    if (!chat) {
      addNotification('Chat not found', 'error');
      return;
    }

    const exportData = {
      chat: chat,
      exportDate: new Date().toISOString(),
      version: '1.0'
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dianav-chat-${chatId}-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    addNotification('Chat exported successfully!', 'success');
  };

  // Delete chat session
  const deleteChat = (chatId: string) => {
    if (window.confirm('Are you sure you want to delete this chat session?')) {
      const updatedChats = chats.filter(c => c.id !== chatId);
      setChats(updatedChats);
      
      // If we deleted the active chat, handle it
      if (activeChatId === chatId) {
        // If there are other chats, switch to the first one
        if (updatedChats.length > 0) {
          setActiveChatId(updatedChats[0].id);
        } else {
          // If no chats left, create a new one after a small delay
          setTimeout(() => {
            handleNewChat();
          }, 100);
        }
      }
      
      addNotification('Chat deleted successfully', 'info');
    }
  };

  const sendMessageToBackend = async (message: string): Promise<ApiResponse> => {
    try {
      // Get current language from i18n
      const currentLanguage = i18n.language || 'en';
      
      const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: message,
          language: currentLanguage
        }),
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

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // Get current language
    const currentLanguage = i18n.language || 'en';

    // Add user message
    const userMsg: ChatMessage = {
      sender: 'user',
      text: userMessage,
      timestamp: new Date()
    };

    // Add streaming message placeholder
    const streamingMsg: ChatMessage = {
      sender: 'ai',
      text: '🤖 Analyzing your request...',
      timestamp: new Date()
    };

    // Update chats with user message and initial streaming message
    setChats(prevChats => {
      const updatedChats = prevChats.map(chat =>
        chat.id === activeChatId
          ? { 
              ...chat, 
              messages: [...chat.messages, userMsg, streamingMsg],
              lastModified: new Date()
            }
          : chat
      );
      return updatedChats;
    });

    // Simulate streaming text generation
    const streamingTexts = [
      '🤖 Analyzing your request...',
      '🔍 Searching diagnostic database...',
      '⚙️ Processing automotive data...',
      '🧠 Generating AI response...',
      '📋 Preparing detailed information...'
    ];

    let currentTextIndex = 0;
    const streamingInterval = setInterval(() => {
      if (currentTextIndex < streamingTexts.length) {
        const currentStreamingText = streamingTexts[currentTextIndex];
        
        // Update the streaming message
        setChats(prevChats => {
          const updatedChats = prevChats.map(chat =>
            chat.id === activeChatId
              ? { 
                  ...chat, 
                  messages: chat.messages.map((msg, index) => 
                    index === chat.messages.length - 1 && msg.sender === 'ai'
                      ? { ...msg, text: currentStreamingText }
                      : msg
                  ),
                  lastModified: new Date()
                }
              : chat
          );
          return updatedChats;
        });
        
        currentTextIndex++;
      }
    }, 800);

    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMessage,
          language: currentLanguage,
        }),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();
      const aiResponse = data.conversational || data.response || 'Sorry, I could not process your request.';

      // Clear streaming interval
      clearInterval(streamingInterval);
      setIsGenerating(false);

      // Start with empty text for typewriter effect
      setChats(prevChats => {
        const updatedChats = prevChats.map(chat =>
          chat.id === activeChatId
            ? { 
                ...chat, 
                messages: chat.messages.map((msg, index) => 
                  index === chat.messages.length - 1 && msg.sender === 'ai'
                    ? { ...msg, text: '' }
                    : msg
                ),
                lastModified: new Date()
              }
            : chat
        );
        return updatedChats;
      });

      // Typewriter effect for AI response text (faster and smoother)
      setIsGenerating(true);
      let currentIndex = 0;
      const totalLen = aiResponse.length;
      const baseDelay = 8; // faster typing
      // Dynamic chunk size: longer texts render more chars per tick (faster overall)
      const chunkSize = Math.min(20, Math.max(3, Math.floor(totalLen / 300)));
      const typewriterInterval = setInterval(() => {
        if (currentIndex < totalLen) {
          currentIndex = Math.min(totalLen, currentIndex + chunkSize);
          const currentText = aiResponse.substring(0, currentIndex);

          setChats(prevChats => {
            const updatedChats = prevChats.map(chat =>
              chat.id === activeChatId
                ? {
                    ...chat,
                    messages: chat.messages.map((msg, index) =>
                      index === chat.messages.length - 1 && msg.sender === 'ai'
                        ? { ...msg, text: currentText }
                        : msg
                    ),
                    lastModified: new Date()
                  }
                : chat
            );
            return updatedChats;
          });
        } else {
          clearInterval(typewriterInterval);
          setIsGenerating(false);
          // After typewriter completes, add diagnostic details and images with smooth transition
          setTimeout(() => {
            setChats(prevChats => {
              const updatedChats = prevChats.map(chat =>
                chat.id === activeChatId
                  ? {
                      ...chat,
                      messages: chat.messages.map((msg, index) =>
                        index === chat.messages.length - 1 && msg.sender === 'ai'
                          ? {
                              ...msg,
                              structured: data.structured || undefined,
                              images: data.images && data.images.length > 0 ? data.images : undefined
                            }
                          : msg
                      ),
                      lastModified: new Date()
                    }
                  : chat
              );
              return updatedChats;
            });
          }, 300); // Small delay before showing diagnostic details
        }
      }, baseDelay);

    } catch (error) {
      console.error('Error in handleSend:', error);
      
      // Clear streaming interval
      clearInterval(streamingInterval);
      
      const errorMsg = "I'm sorry, I encountered an error while processing your request. Please try again.";
      
      // Replace streaming message with error message
      setChats(prevChats => {
        const updatedChats = prevChats.map(chat =>
          chat.id === activeChatId
            ? { 
                ...chat, 
                messages: chat.messages.map((msg, index) => 
                  index === chat.messages.length - 1 && msg.sender === 'ai'
                    ? { ...msg, text: errorMsg }
                    : msg
                ),
                lastModified: new Date()
              }
            : chat
        );
        return updatedChats;
      });
    } finally {
      setIsLoading(false);
    }
    
    if (showWelcome) setShowWelcome(false);
  };

  const handleExampleClick = (q: string) => {
    setInput(q);
    setTimeout(() => handleSend(), 100);
  };

  const handleNewChat = () => {
    const newId = (Date.now() + Math.random()).toString();
    const newChat: ChatSession = {
      id: newId, 
      heading: 'New Chat', 
      messages: [],
      createdAt: new Date(),
      lastModified: new Date()
    };
    setChats(prevChats => [newChat, ...prevChats]);
    setActiveChatId(newId);
    setInput('');
    setShowWelcome(true);
    setChatWindowClass('');
  };

  const renderMessage = (msg: ChatMessage, index: number) => {
    // Dynamic width for AI bubble to smoothly expand with content
    const isAi = msg.sender === 'ai';
    const isLastAi = isAi && index === activeChat.messages.length - 1;
    const currentLen = msg.text ? msg.text.length : 0;
    // Estimate target min-width in ch units based on current text length
    // Ensures a pleasant expansion from ~18ch up to ~72ch as content grows
    const estimatedMinCh = isAi
      ? Math.min(72, Math.max(18, Math.floor((currentLen || (isLastAi && isGenerating ? 1 : 0)) * 0.5)))
      : undefined;

    return (
      <div 
        key={index} 
        className={`dianav-chat-bubble ${msg.sender}`}
        style={{
          opacity: 1,
          visibility: 'visible',
          display: 'block',
          position: 'relative',
          zIndex: 999,
          backgroundColor: msg.sender === 'ai' ? '#2351a2' : '#2d6be6',
          color: 'white',
          padding: '14px 20px',
          borderRadius: '12px',
          marginBottom: '8px',
          maxWidth: '80%',
          minWidth: isAi ? `${estimatedMinCh}ch` : undefined,
          alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
          marginLeft: msg.sender === 'user' ? 'auto' : '0',
          marginRight: msg.sender === 'user' ? '0' : 'auto'
        }}
      >
        <div className="dianav-message-header">
          <span className="dianav-message-sender">
            {msg.sender === 'ai' ? '🤖 AI Assistant' : '👤 You'}
          </span>
          {msg.timestamp && (
            <span className="dianav-message-time">
              {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
        </div>
        
        <div className="dianav-message-text">
          {msg.sender === 'ai' ? (
            <ReactMarkdown>{msg.text}</ReactMarkdown>
          ) : (
            msg.text
          )}
        </div>
        
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
                  onClick={() => handleImageClick(img)}
                  title="Click to enlarge"
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
  };

  return (
    <div className={`dianav-app-wide${sidebarOpen ? '' : ' sidebar-collapsed'}${darkMode ? ' dark-mode' : ''}`}>
      <aside className={`dianav-sidebar${sidebarOpen ? ' open' : ' collapsed'}`}>
        <div className="dianav-sidebar-toggle-row">
          <button className="dianav-sidebar-toggle" onClick={handleSidebarToggle}>
            {sidebarOpen ? '<' : '>'}
          </button>
          <button 
            className="dianav-theme-toggle" 
            onClick={() => setDarkMode(v => !v)}
            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
        
        <div className="dianav-newchat-row">
          {sidebarOpen ? (
            <button className="dianav-newchat-btn" onClick={handleNewChat}>+ {t('common.newChat')}</button>
          ) : (
                          <button className="dianav-newchat-btn-collapsed" title={t('common.newChat')} onClick={handleNewChat}>+</button>
          )}
        </div>
        
        {sidebarOpen && (
          <div className="dianav-chat-list">
            {chats.map(chat => (
              <div key={chat.id} className="dianav-chat-item">
                <div
                  className={`dianav-chat-heading${chat.id === activeChatId ? ' active' : ''}`}
                  onClick={() => { 
                    setActiveChatId(chat.id); 
                    setShowWelcome(chat.messages.length === 0);
                    setTimeout(() => {
                      setChatWindowClass(getChatWindowClass(chat.messages));
                    }, 100);
                  }}
                >
                  <div className="dianav-chat-title">{chat.heading}</div>
                  <div className="dianav-chat-meta">
                    {chat.messages.length} messages • {chat.lastModified.toLocaleDateString()}
                  </div>
                </div>
                <div className="dianav-chat-actions">
                  <button 
                    className="dianav-chat-action-btn"
                    onClick={() => exportChat(chat.id)}
                    title="Export Chat"
                  >
                    📤
                  </button>
                  <button 
                    className="dianav-chat-action-btn"
                    onClick={() => deleteChat(chat.id)}
                    title="Delete Chat"
                  >
                    🗑️
                  </button>
                </div>
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
              <div className="dianav-logo-text">TMPV / TPEM</div>
            </div>
            <div className="dianav-title">DIAGNOSTIC NAVIGATOR</div>
            <div className="dianav-ai-label">AI Assistant</div>
            <div className="dianav-header-actions">
              <LanguageSwitcher />
              <button 
                className="dianav-quick-actions-btn"
                onClick={() => setShowQuickActions(!showQuickActions)}
                title="Quick Actions"
              >
                ⚡
              </button>
            </div>
          </header>
          
          {showQuickActions && (
            <div className="dianav-quick-actions-panel">
              <h3>{t('quickActions.title')}</h3>
              <div className="dianav-quick-actions-grid">
                {quickActions.map((action, index) => (
                  <button
                    key={index}
                    className="dianav-quick-action-btn"
                    onClick={() => handleQuickAction(action.action)}
                  >
                    <div className="dianav-quick-action-icon">{action.label.split(' ')[0]}</div>
                    <div className="dianav-quick-action-label">{t(`quickActions.${action.tKey}`)}</div>
                    <div className="dianav-quick-action-desc">{t(`quickActions.${action.tKey}Desc`)}</div>
                  </button>
                ))}
              </div>
            </div>
          )}
          
          <main className="dianav-main">
            <div
              className={`dianav-welcome${showWelcome ? ' show' : ' hide'}`}
              ref={welcomeRef}
              style={{ pointerEvents: showWelcome ? 'auto' : 'none' }}
            >
              <h1 className="dianav-h1">{t('chat.welcome')}</h1>
              <div className="dianav-subtitle">{t('chat.welcomeSubtitle')}</div>
              
              <div className="dianav-search-filters">
                <input
                  type="text"
                  placeholder={t('common.search')}
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  className="dianav-filter-input"
                />
                <select 
                  value={selectedCategory} 
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="dianav-category-select"
                >
                  <option value="all">All Categories</option>
                  <option value="Common DTCs">{t('exampleQuestions.commonDTCs')}</option>
                  <option value="Symptoms">{t('exampleQuestions.symptoms')}</option>
                  <option value="Quick Search">{t('exampleQuestions.quickSearch')}</option>
                </select>
              </div>
              
              <div className="dianav-example-questions">
                {exampleQuestions
                  .filter(category => selectedCategory === 'all' || category.category === selectedCategory)
                  .flatMap(category => category.questions)
                  .filter(question => 
                    searchFilter === '' || 
                    question.toLowerCase().includes(searchFilter.toLowerCase())
                  )
                  .map((q, i) => (
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
              <div 
                className={`dianav-chat-window${chatWindowClass ? ` ${chatWindowClass}` : ''}${activeChat.messages.length > 0 ? ' has-messages' : ''}`}
                style={{
                  position: 'relative',
                  zIndex: 100,
                  opacity: 1,
                  visibility: 'visible',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                  padding: '24px 16px 16px 16px',
                  overflowY: 'auto',
                  minHeight: activeChat.messages.length > 0 ? '500px' : '200px'
                }}
              >
                {activeChat.messages.map((msg, i) => renderMessage(msg, i))}
                {isLoading && (
                  <div className="dianav-chat-bubble ai">
                    <div className="dianav-loading">
                      <div className="dianav-loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                      <p>{t('chat.typing')}</p>
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>
              
              <form className="dianav-input-row" onSubmit={handleSend} autoComplete="off">
                <input
                  type="text"
                  placeholder={t('chat.placeholder')}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  disabled={isLoading}
                  autoFocus
                />
                <button type="submit" disabled={isLoading}>
                  {isLoading ? (
                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div className="spinner" style={{
                        width: '16px',
                        height: '16px',
                        border: '2px solid #ffffff40',
                        borderTop: '2px solid #ffffff',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }}></div>
                      {t('common.loading')}
                    </span>
                  ) : t('common.send')}
                </button>
              </form>
              
              <footer className="dianav-footer">
                <div className="dianav-footer-content">
                  <span>Powered by Tata Motors</span>
                  <div className="dianav-footer-actions">
                    <button className="dianav-footer-btn" onClick={() => exportChat(activeChatId)}>
                      {t('chat.exportChat')}
                    </button>
                    <button className="dianav-footer-btn" onClick={() => window.print()}>
                      Print Report
                    </button>
                  </div>
                </div>
              </footer>
            </div>
          </main>
        </div>
      </div>

      {showImageModal && selectedImage && (
        <div className="dianav-image-modal-overlay">
          <div className="dianav-image-modal-content">
            <img src={selectedImage.image_data} alt={selectedImage.description} />
            <p>{selectedImage.description} ({t('diagnostic.pageNumber', { number: selectedImage.page_num + 1 })})</p>
            <button onClick={closeImageModal} className="dianav-close-button">X</button>
          </div>
        </div>
      )}

      {/* Notifications */}
      <div className="dianav-notifications">
        {notifications.map(notification => (
          <div 
            key={notification.id} 
            className={`dianav-notification dianav-notification-${notification.type}`}
            onClick={() => removeNotification(notification.id)}
          >
            <span className="dianav-notification-message">{notification.message}</span>
            <button className="dianav-notification-close">×</button>
          </div>
        ))}
      </div>
      
      {/* Vercel Analytics */}
      <Analytics />
    </div>
  );
}

export default App;
