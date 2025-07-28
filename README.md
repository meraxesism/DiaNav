# DiaNav - AI-Powered Automotive Diagnostic Assistant

<div align="center">

![DiaNav Logo](dianav-frontend/public/tata-logo.png)

**Advanced AI Diagnostic System for Automotive Troubleshooting**

[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-green.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-LLM-orange.svg)](https://ollama.ai/)
[![License](https://img.shields.io/badge/License-AGPL%20v3-red.svg)](LICENSE)

</div>

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

## 🚀 Project Overview

**DiaNav** is a sophisticated AI-powered diagnostic assistant designed for automotive professionals. Built with modern web technologies and advanced AI integration, it provides intelligent troubleshooting guidance for diagnostic trouble codes (DTCs) and automotive systems.

### Key Features
- 🤖 **AI-Powered Diagnostics**: Local LLM integration with Ollama for conversational responses
- 🔍 **Semantic Vector Search**: Advanced search using sentence-transformers for natural language queries
- 💬 **Interactive Chat Interface**: Modern, responsive UI with real-time conversations
- 🎯 **Intelligent Search**: Fuzzy matching and vector search for DTC codes and symptoms
- 📱 **Professional UI/UX**: Enterprise-grade interface with collapsible sidebar
- 🔄 **Multi-Session Management**: Support for multiple diagnostic sessions
- 📊 **Structured Data Processing**: Efficient parsing and indexing of diagnostic data
- 🖼️ **Secure Image Display**: Confidential diagrams displayed in memory only
- 📝 **Markdown Rendering**: Rich text formatting for AI responses
- 🔍 **Image Modal**: Clickable diagnostic images with enlargement capability
- 🚀 **One-Click Startup**: Automated deployment scripts for easy setup

---

## 🏗️ Architecture & Technology Stack

### Frontend
- **React 18** with TypeScript for type-safe development
- **ReactMarkdown** for rich text rendering of AI responses
- **Modern CSS** with Flexbox layouts and CSS Grid
- **Responsive Design** optimized for desktop applications
- **State Management** using React Hooks (useState, useEffect, useRef)
- **Professional UI Components** with smooth animations and transitions

### Backend
- **FastAPI** (Python) for high-performance REST API
- **Ollama Integration** for local LLM processing
- **Sentence-Transformers** for local vector embeddings
- **Pydantic** for data validation and serialization
- **Regex Pattern Matching** for intelligent DTC code extraction
- **Modular Architecture** with separate data processing layer
- **PyMuPDF** for secure PDF image extraction (memory-only processing)

### AI & Search Capabilities
- **Local LLM Processing** using Ollama (llama3.2:3b model)
- **Vector Search** with cosine similarity for semantic matching
- **Fuzzy Search** with fallback mechanisms
- **Conversational AI** for casual user interactions
- **Structured Response Generation** with markdown formatting

### Data Processing
- **Structured Data Parsing** from automotive diagnostic documents
- **Intelligent Indexing** for fast query responses
- **Dual Response Format**: Conversational + Structured output
- **Error Handling** with graceful fallbacks
- **Secure Image Processing** with no disk storage

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

### 2. **Advanced Search Capabilities**
- Vector search using sentence-transformers
- Fuzzy search with fallback mechanisms
- Semantic understanding of user queries
- Multi-modal search (code, symptoms, descriptions)

### 3. **Enhanced UI/UX**
- ReactMarkdown for rich text rendering
- Dynamic chat window expansion
- Image modal for enlarged diagnostic diagrams
- Professional styling with hover effects
- Responsive design for all screen sizes

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

### 6. **Intelligent Data Processing**
- Regex-based DTC code extraction
- Structured data parsing and indexing
- Dual response format (conversational + structured)
- Error handling with graceful fallbacks

---

## 🎨 Design Philosophy

### User Experience
- **Intuitive Interface**: Clean, professional design suitable for enterprise use
- **Responsive Layout**: Optimized for desktop diagnostic workstations
- **Accessibility**: High contrast, readable typography, keyboard navigation
- **Conversational AI**: Natural interaction patterns

### Technical Excellence
- **Type Safety**: Full TypeScript implementation
- **Performance**: Optimized rendering and state management
- **Maintainability**: Clean code architecture with separation of concerns
- **Security**: Memory-only processing of confidential data
- **Local Processing**: No external dependencies for sensitive operations

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

## 🚀 Future Enhancements

### Planned Features
- **Advanced ML Models**: Fine-tuned models for automotive diagnostics
- **Real-time Diagnostics**: Live vehicle data integration
- **Mobile Application**: Cross-platform diagnostic tool
- **Advanced Analytics**: Diagnostic pattern recognition
- **Multi-language Support**: International automotive standards
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

### Code Quality
- **Clean Architecture**: Separation of concerns
- **Type Safety**: Full TypeScript implementation
- **Responsive Design**: Mobile-first approach
- **Performance Optimization**: Efficient rendering and state updates
- **Maintainable Code**: Clear structure and documentation
- **Security Best Practices**: Memory-only processing of sensitive data
- **AI Best Practices**: Local processing for confidentiality

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