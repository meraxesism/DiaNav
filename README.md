# DiaNav - AI-Powered Automotive Diagnostic Assistant

<div align="center">

![DiaNav Logo](dianav-frontend/public/tata-logo.png)

**Advanced AI Diagnostic System for Automotive Troubleshooting**

[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-green.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-AGPL%20v3-red.svg)](LICENSE)

</div>

---

## 🚀 Project Overview

**DiaNav** is a sophisticated AI-powered diagnostic assistant designed for automotive professionals. Built with modern web technologies and AI integration, it provides intelligent troubleshooting guidance for diagnostic trouble codes (DTCs) and automotive systems.

### Key Features
- 🤖 **AI-Powered Diagnostics**: Natural language processing for automotive queries
- 💬 **Interactive Chat Interface**: Modern, responsive UI with real-time conversations
- 🔍 **Intelligent Search**: Advanced pattern matching for DTC codes and symptoms
- 📱 **Professional UI/UX**: Enterprise-grade interface with collapsible sidebar
- 🔄 **Multi-Session Management**: Support for multiple diagnostic sessions
- 📊 **Structured Data Processing**: Efficient parsing and indexing of diagnostic data

---

## 🏗️ Architecture & Technology Stack

### Frontend
- **React 18** with TypeScript for type-safe development
- **Modern CSS** with Flexbox layouts and CSS Grid
- **Responsive Design** optimized for desktop applications
- **State Management** using React Hooks (useState, useEffect, useRef)
- **Professional UI Components** with smooth animations and transitions

### Backend
- **FastAPI** (Python) for high-performance REST API
- **Pydantic** for data validation and serialization
- **Regex Pattern Matching** for intelligent DTC code extraction
- **Modular Architecture** with separate data processing layer

### Data Processing
- **Structured Data Parsing** from automotive diagnostic documents
- **Intelligent Indexing** for fast query responses
- **Dual Response Format**: Conversational + Structured output
- **Error Handling** with graceful fallbacks

---

## 🎯 Technical Highlights

### Advanced UI/UX Implementation
```typescript
// Multi-session chat management with TypeScript
interface ChatSession {
  id: string;
  heading: string;
  messages: ChatMessage[];
}

// Responsive sidebar with smooth animations
const [sidebarOpen, setSidebarOpen] = useState(true);
```

### Intelligent Backend Processing
```python
# Advanced DTC pattern matching with regex
def find_dtc_code_in_query(query: str):
    match = re.search(r"([A-Z][0-9A-Z]{3,}-?\d{0,2})", query)
    return match.group(1) if match else None
```

### Professional CSS Architecture
```css
/* Modern flexbox layout with responsive design */
.dianav-app-wide {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #184077 0%, #15325c 100%);
}
```

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Git

### Frontend Setup
```bash
cd dianav-frontend
npm install
npm start
```

### Backend Setup
```bash
pip install -r requirements.txt
python dianav_backend.py
```

### Development Server
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

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
├── requirements.txt         # Python dependencies
├── sample_dtc_data.txt      # Demo data for testing
└── README.md               # Project documentation
```

---

## 🔧 Key Technical Implementations

### 1. **Responsive Chat Interface**
- Real-time message handling with auto-scroll
- Professional chat bubbles with user/AI distinction
- Smooth animations and transitions

### 2. **Advanced State Management**
- Multi-session chat history
- Dynamic sidebar collapse/expand
- Welcome screen with animated transitions

### 3. **Intelligent Data Processing**
- Regex-based DTC code extraction
- Structured data parsing and indexing
- Dual response format (conversational + structured)

### 4. **Professional UI Components**
- Collapsible sidebar with smooth animations
- Auto-generated chat headings
- Professional color scheme and typography

---

## 🎨 Design Philosophy

### User Experience
- **Intuitive Interface**: Clean, professional design suitable for enterprise use
- **Responsive Layout**: Optimized for desktop diagnostic workstations
- **Accessibility**: High contrast, readable typography, keyboard navigation

### Technical Excellence
- **Type Safety**: Full TypeScript implementation
- **Performance**: Optimized rendering and state management
- **Maintainability**: Clean code architecture with separation of concerns

---

## 🔒 Security & Data Protection

- **Sensitive Data Protection**: Company diagnostic data excluded from public repository
- **Sample Data**: Demo functionality with mock data for testing
- **Professional Licensing**: AGPL v3 license for open collaboration

---

## 🚀 Future Enhancements

### Planned Features
- **Machine Learning Integration**: Advanced AI for symptom analysis
- **Real-time Diagnostics**: Live vehicle data integration
- **Mobile Application**: Cross-platform diagnostic tool
- **Advanced Analytics**: Diagnostic pattern recognition
- **Multi-language Support**: International automotive standards

### Technical Roadmap
- **Microservices Architecture**: Scalable backend services
- **Real-time Communication**: WebSocket integration
- **Advanced Caching**: Redis for performance optimization
- **Containerization**: Docker deployment support

---

## 👨‍💻 Development Experience

### Skills Demonstrated
- **Full-Stack Development**: React + FastAPI integration
- **TypeScript Expertise**: Type-safe development practices
- **Modern CSS**: Flexbox, Grid, animations, responsive design
- **API Design**: RESTful API with proper error handling
- **State Management**: Complex UI state with React Hooks
- **Data Processing**: Regex, parsing, indexing algorithms
- **Professional UI/UX**: Enterprise-grade interface design

### Code Quality
- **Clean Architecture**: Separation of concerns
- **Type Safety**: Full TypeScript implementation
- **Responsive Design**: Mobile-first approach
- **Performance Optimization**: Efficient rendering and state updates
- **Maintainable Code**: Clear structure and documentation

---

## 📞 Contact & Collaboration

This project demonstrates advanced full-stack development capabilities suitable for enterprise applications. The architecture showcases:

- **Scalable Design**: Modular components ready for expansion
- **Professional Standards**: Enterprise-grade code quality
- **Modern Technologies**: Latest React, TypeScript, and FastAPI
- **User-Centric Approach**: Intuitive interface for complex workflows

---

<div align="center">

**Built with ❤️ for Automotive Excellence**

*Professional diagnostic solutions for the modern automotive industry*

</div> 