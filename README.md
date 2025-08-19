# DiaNav - AI-Powered Automotive Diagnostic Assistant

<div align="center">

# 🚗 DiaNav

**Advanced AI-Powered Automotive Diagnostic Assistant**

*Intelligent Diagnostic System for Professional Automotive Troubleshooting*

[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-green.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-LLM-orange.svg)](https://ollama.ai/)
[![License](https://img.shields.io/badge/License-AGPL%20v3-red.svg)](LICENSE)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/meraxesism/DiaNav)](https://github.com/meraxesism/DiaNav/releases)
[![GitHub stars](https://img.shields.io/github/stars/meraxesism/DiaNav)](https://github.com/meraxesism/DiaNav/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/meraxesism/DiaNav)](https://github.com/meraxesism/DiaNav/network)
[![GitHub issues](https://img.shields.io/github/issues/meraxesism/DiaNav)](https://github.com/meraxesism/DiaNav/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/meraxesism/DiaNav)](https://github.com/meraxesism/DiaNav/pulls)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)](https://github.com/meraxesism/DiaNav/actions)
[![Coverage](https://img.shields.io/badge/Coverage-99%25-brightgreen)](https://github.com/meraxesism/DiaNav/tree/main/tests)
[![Security](https://img.shields.io/badge/Security-Scanned-blue)](https://github.com/meraxesism/DiaNav/security)

</div>

---

## 📚 Table of Contents
- [📋 Ownership & Licensing Disclaimer](#-ownership--licensing-disclaimer)
- [🔒 Security Notice](#-security-notice---confidential-data-handling)
- [📊 Project Status & Progress](#-project-status--progress)
- [🚀 Project Overview](#-project-overview)
- [🏗️ Architecture & Technology Stack](#️-architecture--technology-stack)
- [🎯 Technical Highlights](#-technical-highlights)
- [🚀 Getting Started](#-getting-started)
- [📁 Project Structure](#-project-structure)
- [🔧 Key Technical Implementations](#-key-technical-implementations)
- [🎨 Design Philosophy](#-design-philosophy)
- [🔒 Security & Data Protection](#-security--data-protection)
- [🆕 Recent Improvements](#-recent-improvements)
- [🚀 Future Enhancements](#-future-enhancements)
- [👨‍💻 Development Experience](#-development-experience)
- [📞 Contact & Collaboration](#-contact--collaboration)

---

## 📋 **OWNERSHIP & LICENSING DISCLAIMER**

**This project was developed as part of an internship at Tata Motors – Digitalization in Quality Assurance. All frontend and UI assets were originally created by Apurv Bhosale.**

This code is licensed under the AGPL v3 License. Any internal or commercial use must comply with this license, including proper attribution and source disclosure.

---

## 🔒 **SECURITY NOTICE - CONFIDENTIAL DATA HANDLING**

**⚠️ IMPORTANT:** This application processes confidential automotive diagnostic data including:
- **Diagnostic Trouble Codes (DTCs)** from proprietary manuals
- **Technical diagrams and schematics** from PDF documents
- **Company-specific diagnostic procedures**

### **Security Measures Implemented:**
- ✅ **No confidential data** is committed to this public repository
- ✅ **Images are processed in memory only** - never saved to disk
- ✅ **PDF files are excluded** from version control
- ✅ **Sample data only** is used for demonstration
- ✅ **All sensitive files** are properly gitignored
- ✅ **Local AI processing** - no external API calls for sensitive data

### **For Production Use:**
- Replace sample data with actual diagnostic files
- Ensure proper access controls and authentication
- Implement additional security measures as required
- Follow company data protection policies

---

## 📊 Project Status & Progress

<div align="center">

### **Current Development Status**

| Component | Progress | Status | Key Features |
|-----------|----------|--------|--------------|
| **Frontend** | **100%** | 🟢 **Complete** | React + TypeScript, Dark Mode, Dynamic UI, Session Management |
| **Backend** | **99%** | 🟢 **Advanced** | FastAPI, AI Integration, Vector Search, Quick Actions |
| **AI/ML** | **100%** | 🟢 **Advanced** | Local LLM, Vector Search, Intelligent Responses |
| **UI/UX** | **100%** | 🟢 **Complete** | Professional Design, Responsive, Accessibility |
| **Security** | **100%** | 🟢 **Complete** | Memory-only Processing, Local AI, Data Protection |

</div>

**🔄 Recent Major Updates:**
- ✅ **Intelligent Quick Actions** with structured responses
- ✅ **Enhanced UI/UX** with dynamic sizing and dark mode
- ✅ **Advanced Session Management** with persistence
- ✅ **Professional Polish** with enterprise-grade interface
- ✅ **Robust Error Handling** and user feedback

---

## 🚀 Project Overview

**DiaNav** is a sophisticated AI-powered diagnostic assistant designed for automotive professionals. Built with modern web technologies and advanced AI integration, it provides intelligent troubleshooting guidance for diagnostic trouble codes (DTCs) and automotive systems.

### Key Features
- 🌍 **Multi-Language Support**: Full internationalization with Hindi and Marathi translations
- 🤖 **AI-Powered Diagnostics**: Local LLM integration with Ollama for conversational responses
- 🎯 **Intelligent Quick Actions**: Smart handling of common diagnostic requests with structured responses
- 🔍 **Semantic Vector Search**: Advanced search using sentence-transformers for natural language queries
- 💬 **Interactive Chat Interface**: Modern, responsive UI with real-time conversations and dynamic sizing
- 🎯 **Intelligent Search**: Fuzzy matching and vector search for DTC codes and symptoms
- 📱 **Professional UI/UX**: Enterprise-grade interface with collapsible sidebar and dark mode
- 🔄 **Multi-Session Management**: Support for multiple diagnostic sessions with export/delete capabilities
- 📊 **Structured Data Processing**: Efficient parsing and indexing of diagnostic data
- 🖼️ **Secure Image Display**: Confidential diagrams displayed in memory only
- 📝 **Markdown Rendering**: Rich text formatting for AI responses
- 🔍 **Image Modal**: Clickable diagnostic images with enlargement capability
- 🚀 **One-Click Startup**: Automated deployment scripts for easy setup
- 🎨 **Enhanced Responsive Design**: Optimized horizontal and vertical spacing for better usability
- 🔧 **Advanced State Management**: Robust chat session handling with localStorage persistence
- 🌐 **Language-Aware AI**: AI responses automatically translated while preserving technical terms

---

## 🏗️ Architecture & Technology Stack

### Frontend
- **React 18** with TypeScript for type-safe development
- **ReactMarkdown** for rich text rendering of AI responses
- **Modern CSS** with Flexbox layouts and CSS Grid
- **Responsive Design** optimized for desktop applications with dynamic sizing
- **State Management** using React Hooks (useState, useEffect, useRef)
- **Professional UI Components** with smooth animations and transitions
- **Dark Mode Support** with theme toggle functionality
- **Advanced Chat Management** with session persistence and export capabilities
- **Dynamic Layout** with collapsible sidebar and optimized spacing

### Backend
- **FastAPI** (Python) for high-performance REST API
- **Ollama Integration** for local LLM processing
- **Sentence-Transformers** for local vector embeddings
- **Pydantic** for data validation and serialization
- **Regex Pattern Matching** for intelligent DTC code extraction
- **Modular Architecture** with separate data processing layer
- **PyMuPDF** for secure PDF image extraction (memory-only processing)
- **Intelligent Quick Action Handling** with structured response generation
- **Enhanced CORS Configuration** supporting multiple frontend ports
- **Advanced Error Handling** with graceful fallbacks and user-friendly messages

### AI & Search Capabilities
- **Local LLM Processing** using Ollama (llama3.2:3b model)
- **Vector Search** with cosine similarity for semantic matching
- **Fuzzy Search** with fallback mechanisms
- **Conversational AI** for casual user interactions
- **Structured Response Generation** with markdown formatting
- **Intelligent Quick Action Routing** with dedicated handler functions
- **Enhanced Response Quality** with professional diagnostic explanations
- **Multi-Modal Response Format** combining conversational and structured data

### Data Processing
- **Structured Data Parsing** from automotive diagnostic documents
- **Intelligent Indexing** for fast query responses
- **Dual Response Format**: Conversational + Structured output
- **Error Handling** with graceful fallbacks
- **Secure Image Processing** with no disk storage
- **Advanced Session Management** with persistent chat history
- **Export Functionality** for diagnostic reports and chat sessions
- **Real-time Data Validation** and sanitization

---

## 🎯 Technical Highlights

### Advanced AI Integration
```python
# Local LLM processing with Ollama
def call_ollama_llm(prompt: str) -> str:
    """
    SECURITY: All AI processing is done locally.
    No external API calls for confidential data.
    """
    # Local LLM response generation
    return structured_response
```

### System Architecture
```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React UI]
        Chat[Chat Interface]
        Sidebar[Sidebar Management]
        Theme[Dark/Light Theme]
    end
    
    subgraph "Backend Layer"
        API[FastAPI Server]
        Query[Query Handler]
        QuickActions[Quick Actions]
        CORS[CORS Middleware]
    end
    
    subgraph "AI/ML Layer"
        Ollama[Ollama LLM]
        VectorSearch[Vector Search]
        Embeddings[Sentence Transformers]
    end
    
    subgraph "Data Layer"
        DTCData[DTC Data Parser]
        PDFExtract[PDF Image Extraction]
        JSONLayout[JSON Layout Data]
        LocalStorage[Local Storage]
    end
    
    UI --> API
    Chat --> Query
    Sidebar --> LocalStorage
    API --> Ollama
    API --> VectorSearch
    VectorSearch --> Embeddings
    API --> DTCData
    DTCData --> PDFExtract
    PDFExtract --> JSONLayout
```

### Semantic Vector Search
```python
# Local vector search using sentence-transformers
class LocalVectorSearch:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings = self.create_dtc_embeddings()
    
    def semantic_search(self, query: str) -> List[Dict]:
        # Cosine similarity search
        return similar_dtcs
```

### Enhanced UI/UX Implementation
```typescript
// Multi-session chat management with TypeScript
interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  images?: DiagnosticImage[];  // Secure image display
  structured?: string;
}

// Dynamic chat window expansion
const getChatWindowClass = () => {
  return messageCount > 5 ? 'expanded' : 'normal';
};
```

### Professional CSS Architecture
```css
/* Secure image display with professional styling */
.dianav-diagnostic-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: transform 0.2s ease;
}

.dianav-diagnostic-image:hover {
  transform: scale(1.02);
}
```

---

## 🌍 Multi-Language Support

DiaNav now supports **full internationalization** with Hindi and Marathi translations, making it accessible to a wider range of automotive professionals.

### Supported Languages
- 🇺🇸 **English** - Primary language
- 🇮🇳 **Hindi** - हिंदी
- 🇮🇳 **Marathi** - मराठी

### Key Features
- 🌐 **Language Switcher**: Elegant dropdown with flag icons and native language names
- 🤖 **AI Response Translation**: Automatic translation of AI responses while preserving technical terms
- 📱 **UI Translation**: Complete interface translation including buttons, labels, and messages
- 🔧 **Technical Term Preservation**: DTC codes, numbers, and technical terms remain unchanged
- 💾 **Language Persistence**: Selected language saved in localStorage
- ⚡ **Performance Optimized**: Translation caching for improved response times

### Implementation Details
```typescript
// Language switcher component with flag icons
const LanguageSwitcher: React.FC = () => {
  const languages = [
    { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸' },
    { code: 'hi', name: 'Hindi', nativeName: 'हिंदी', flag: '🇮🇳' },
    { code: 'mr', name: 'Marathi', nativeName: 'मराठी', flag: '🇮🇳' }
  ];
  
  const handleLanguageChange = (languageCode: string) => {
    i18n.changeLanguage(languageCode);
    localStorage.setItem('language', languageCode);
  };
};
```

### Backend Translation API
```python
def translate_ai_response(text: str, target_language: str) -> str:
    """Translate AI response while preserving numbers, DTC codes, and technical terms."""
    if target_language == "en":
        return text
    
    # Preserve technical terms by temporarily replacing them
    technical_terms = ['LIN', 'CAN', 'ECU', 'ABS', 'ESP', 'TCS', 'VIN', 'OBD', 'DTC']
    # ... translation logic with term preservation
    return translated_text
```

### Translation File Structure
```json
{
  "common": {
    "newChat": "New Chat",
    "search": "Search",
    "send": "Send"
  },
  "chat": {
    "welcome": "Welcome to DiaNav",
    "placeholder": "Ask about diagnostic codes, symptoms, or troubleshooting..."
  },
  "diagnostic": {
    "dtcCode": "DTC Code",
    "description": "Description",
    "symptoms": "Symptoms"
  }
}
```

---

## 📸 Screenshots & Demo

<div align="center">

### **DiaNav in Action**

| Feature | Screenshot | Description |
|---------|------------|-------------|
| **Main Interface** | ![Main Chat Interface](docs/screenshots/ui/main-chat-interface.png) | Full-screen chat interface with AI responses |
| **Dark Mode** | ![Dark Mode](docs/screenshots/ui/dark-mode-interface.png) | Professional dark theme for extended use |
| **Quick Actions** | ![Quick Actions](docs/screenshots/features/quick-actions-panel.png) | Intelligent quick action panel |
| **Image Modal** | ![Image Modal](docs/screenshots/features/image-modal-hover.png) | Diagnostic image enlargement |
| **Session Export** | ![Session Export](docs/screenshots/features/session-export.png) | Chat session export functionality |

</div>

### **🌐 Live Demo (Frontend Only)**
**[🚀 Try DiaNav Frontend](https://dia-nav.vercel.app/)**

*Experience the frontend interface - Backend requires local setup with Ollama - Desktop only deployment temporarily*

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Git
- Ollama (for LLM functionality)

### Quick Start (Recommended)
```bash
# Clone the repository
git clone https://github.com/meraxesism/DiaNav.git
cd DiaNav

# Install Ollama and pull the model
# Follow instructions at https://ollama.ai/
ollama pull llama3.2:3b

# Start DiaNav with one command
powershell -ExecutionPolicy Bypass -File "start_dianav.ps1"
```

### Manual Setup

#### Frontend Setup
```bash
cd dianav-frontend
npm install
npm start
```

#### Backend Setup
```bash
pip install -r requirements.txt
python dianav_backend.py
```

### Development Server
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Health: http://localhost:8000/health

---

## 📁 Project Structure

```
DiaNavv2/
├── dianav-frontend/          # React TypeScript frontend
│   ├── src/
│   │   ├── App.tsx          # Main application component
│   │   ├── App.css          # Professional styling
│   │   └── index.tsx        # Application entry point
│   └── public/
│       └── tata-logo.png    # Brand assets
├── dianav_backend.py         # FastAPI backend server
├── dianav_data.py           # Data processing utilities
├── local_vector_search.py   # Vector search implementation
├── requirements.txt         # Python dependencies
├── start_dianav.ps1        # PowerShell startup script
├── start_dianav.bat        # Windows batch startup script
├── stop_dianav.ps1         # PowerShell stop script
├── VECTOR_SEARCH_README.md # Vector search documentation
├── STARTUP_GUIDE.md        # Startup guide
├── sample_dtc_data.txt     # Demo data for testing
├── .gitignore             # Security: excludes confidential files
└── README.md              # Project documentation
```

---

## 🔧 Key Technical Implementations

### 1. **AI-Powered Conversational Interface**
- Local LLM integration with Ollama
- Structured response generation with markdown
- Casual conversation handling ("hey", "bro", etc.)
- Professional diagnostic explanations
- Intelligent quick action handling with structured responses
- Enhanced response quality with detailed diagnostic information

### 2. **Advanced Search Capabilities**
- Vector search using sentence-transformers
- Fuzzy search with fallback mechanisms
- Semantic understanding of user queries
- Multi-modal search (code, symptoms, descriptions)

### 3. **Enhanced UI/UX**
- ReactMarkdown for rich text rendering
- Dynamic chat window expansion with conditional sizing
- Image modal for enlarged diagnostic diagrams
- Professional styling with hover effects
- Responsive design for all screen sizes
- Dark mode support with theme toggle
- Optimized horizontal and vertical spacing
- Collapsible sidebar with proper button positioning
- Advanced chat session management with export/delete

### 4. **Secure Image Processing**
- Memory-only image extraction from PDFs
- Bounding box optimization for quality
- Base64 encoding for web display
- No disk storage of confidential images
- Professional image display with descriptions

### 5. **Automated Deployment**
- One-click startup scripts
- Process management and monitoring
- Cross-platform compatibility
- Easy development setup
- Enhanced CORS configuration for multiple ports
- Robust error handling and recovery

### 6. **Intelligent Data Processing**
- Regex-based DTC code extraction
- Structured data parsing and indexing
- Dual response format (conversational + structured)
- Error handling with graceful fallbacks
- Advanced session persistence with localStorage
- Export functionality for diagnostic reports
- Real-time data validation and sanitization

---

## 🎨 Design Philosophy

### User Experience
- **Intuitive Interface**: Clean, professional design suitable for enterprise use
- **Responsive Layout**: Optimized for desktop diagnostic workstations with dynamic sizing
- **Accessibility**: High contrast, readable typography, keyboard navigation
- **Conversational AI**: Natural interaction patterns
- **Enhanced Usability**: Optimized spacing and layout for better workflow
- **Professional Polish**: Enterprise-grade interface with attention to detail

### Technical Excellence
- **Type Safety**: Full TypeScript implementation
- **Performance**: Optimized rendering and state management
- **Maintainability**: Clean code architecture with separation of concerns
- **Security**: Memory-only processing of confidential data
- **Local Processing**: No external dependencies for sensitive operations
- **Robust State Management**: Advanced chat session handling with persistence
- **Enhanced Error Handling**: Graceful fallbacks and user-friendly error messages
- **Scalable Architecture**: Modular design ready for future enhancements

---

## 🔒 Security & Data Protection

- **Confidential Data Protection**: All sensitive files excluded from repository
- **Memory-Only Processing**: Images processed in RAM, never saved to disk
- **Local AI Processing**: All LLM operations performed locally
- **Sample Data**: Demo functionality with mock data for testing
- **Professional Licensing**: AGPL v3 license for open collaboration
- **Secure Architecture**: No persistent storage of confidential information
- **Vector Search Security**: Local embeddings, no external API calls

---

## 🆕 Recent Improvements (Latest Update)

### 🌍 Multi-Language Support (NEW!)
- **Full Internationalization**: Complete Hindi and Marathi language support
- **Language Switcher**: Elegant dropdown with flag icons and native language names
- **AI Response Translation**: Automatic translation while preserving technical terms
- **UI Translation**: Complete interface translation including all buttons and labels
- **Technical Term Preservation**: DTC codes, numbers, and technical terms remain unchanged
- **Language Persistence**: Selected language saved in localStorage
- **Translation Caching**: Performance optimization with translation caching

### Enhanced AI Intelligence
- **Intelligent Quick Actions**: Smart handling of common diagnostic requests with structured, professional responses
- **Enhanced Response Quality**: Improved AI responses with detailed diagnostic explanations
- **Advanced Error Handling**: Graceful fallbacks and user-friendly error messages
- **Language-Aware Responses**: AI responses automatically translated based on user preference

### Improved User Interface
- **Dynamic Chat Window**: Conditional vertical expansion for better response visibility
- **Optimized Spacing**: Enhanced horizontal and vertical spacing for improved usability
- **Dark Mode Support**: Theme toggle functionality with proper positioning
- **Responsive Design**: Better layout adaptation for different screen sizes
- **Language Switcher Integration**: Seamless language selection in header

### Advanced Session Management
- **Persistent Chat Sessions**: Robust localStorage-based session persistence
- **Export Functionality**: Chat session export and diagnostic report generation
- **Enhanced Deletion**: Proper chat session removal with state management
- **Multi-Port Support**: CORS configuration supporting multiple frontend ports

### Professional Polish
- **Enterprise-Grade UI**: Enhanced visual hierarchy and component spacing
- **Improved Accessibility**: Better keyboard navigation and user feedback
- **Performance Optimization**: Efficient rendering and state updates
- **Scalable Architecture**: Modular design ready for future enhancements
- **Internationalization Ready**: Built with i18n best practices

---

## 🚀 Future Enhancements

### Planned Features
- **Advanced ML Models**: Fine-tuned models for automotive diagnostics
- **Real-time Diagnostics**: Live vehicle data integration
- **Mobile Application**: Cross-platform diagnostic tool
- **Advanced Analytics**: Diagnostic pattern recognition
- **Additional Languages**: Support for more regional languages (Gujarati, Tamil, etc.)
- **Voice Interface**: Speech-to-text and text-to-speech capabilities

### Technical Roadmap
- **Microservices Architecture**: Scalable backend services
- **Real-time Communication**: WebSocket integration
- **Advanced Caching**: Redis for performance optimization
- **Containerization**: Docker deployment support
- **Enhanced Security**: Additional authentication and authorization
- **Model Optimization**: Quantized models for better performance

---

## 👨‍💻 Development Experience

### Skills Demonstrated
- **Full-Stack Development**: React + FastAPI integration
- **AI/ML Integration**: Local LLM and vector search implementation
- **TypeScript Expertise**: Type-safe development practices
- **Modern CSS**: Flexbox, Grid, animations, responsive design
- **API Design**: RESTful API with proper error handling
- **State Management**: Complex UI state with React Hooks
- **Data Processing**: Regex, parsing, indexing algorithms
- **Professional UI/UX**: Enterprise-grade interface design
- **Security Implementation**: Confidential data handling
- **DevOps**: Automated deployment and process management
- **Advanced UI/UX**: Dynamic layouts, dark mode, responsive design
- **Session Management**: Persistent chat sessions with export capabilities
- **Error Handling**: Robust error management and user feedback
- **Performance Optimization**: Efficient rendering and state updates
- **Internationalization**: Multi-language support with react-i18next
- **Translation Services**: Backend translation API with Llama 3

### Code Quality
- **Clean Architecture**: Separation of concerns
- **Type Safety**: Full TypeScript implementation
- **Responsive Design**: Mobile-first approach
- **Performance Optimization**: Efficient rendering and state updates
- **Maintainable Code**: Clear structure and documentation
- **Security Best Practices**: Memory-only processing of sensitive data
- **AI Best Practices**: Local processing for confidentiality
- **Enhanced User Experience**: Optimized layouts and interactions
- **Robust Error Handling**: Comprehensive error management
- **Scalable Design**: Modular components for future expansion

---

## 📞 Contact & Collaboration

This project demonstrates advanced full-stack development capabilities suitable for enterprise applications. The architecture showcases:

- **Scalable Design**: Modular components ready for expansion
- **Professional Standards**: Enterprise-grade code quality
- **Modern Technologies**: Latest React, TypeScript, FastAPI, and AI
- **User-Centric Approach**: Intuitive interface for complex workflows
- **Security Awareness**: Proper handling of confidential data
- **AI Integration**: Local processing for data privacy

---

<div align="center">

**Built with ❤️ for Automotive Excellence**

*Professional diagnostic solutions for the modern automotive industry*

</div> 
