# DiaNav Architecture Documentation

This folder contains architecture diagrams and technical documentation for the DiaNav project.

## 🏗️ System Architecture

### High-Level Architecture
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

### Data Flow Architecture
```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant O as Ollama
    participant V as Vector Search
    participant D as Data Parser
    
    U->>F: Send Query
    F->>B: POST /query
    B->>B: Check Quick Actions
    alt Quick Action Detected
        B->>B: Handle Quick Action
    else DTC Query
        B->>D: Parse DTC Data
        B->>V: Semantic Search
        V->>B: Return Results
        B->>O: Generate Response
        O->>B: AI Response
    end
    B->>F: Structured Response
    F->>U: Display Results
```

### Component Architecture
```mermaid
graph LR
    subgraph "Frontend Components"
        App[App.tsx]
        Chat[ChatWindow]
        Sidebar[Sidebar]
        Input[InputRow]
        Modal[ImageModal]
    end
    
    subgraph "Backend Services"
        QueryService[Query Service]
        VectorService[Vector Service]
        ImageService[Image Service]
        ExportService[Export Service]
    end
    
    subgraph "Data Models"
        DTC[DTC Model]
        ChatSession[Chat Session]
        UserQuery[User Query]
        AIResponse[AI Response]
    end
    
    App --> Chat
    App --> Sidebar
    Chat --> Input
    Chat --> Modal
    QueryService --> VectorService
    QueryService --> ImageService
    QueryService --> ExportService
    VectorService --> DTC
    QueryService --> ChatSession
```

## 🔐 Security Architecture

### Data Flow Security
```mermaid
graph TB
    subgraph "Secure Data Handling"
        Input[User Input]
        Validation[Input Validation]
        Sanitization[Data Sanitization]
        Processing[Local Processing]
        Output[Secure Output]
    end
    
    subgraph "Memory-Only Processing"
        PDF[PDF Files]
        Images[Images]
        Memory[RAM Processing]
        NoDisk[No Disk Storage]
    end
    
    subgraph "Local AI Processing"
        Ollama[Ollama LLM]
        Vector[Vector Search]
        Local[Local Embeddings]
        NoAPI[No External APIs]
    end
    
    Input --> Validation
    Validation --> Sanitization
    Sanitization --> Processing
    Processing --> Output
    PDF --> Memory
    Images --> Memory
    Memory --> NoDisk
    Ollama --> Local
    Vector --> Local
    Local --> NoAPI
```

## 📊 Performance Architecture

### Caching Strategy
```mermaid
graph LR
    subgraph "Frontend Cache"
        LocalStorage[LocalStorage]
        SessionStorage[SessionStorage]
        MemoryCache[Memory Cache]
    end
    
    subgraph "Backend Cache"
        EmbeddingCache[Embedding Cache]
        DTCCache[DTC Cache]
        ResponseCache[Response Cache]
    end
    
    LocalStorage --> SessionStorage
    SessionStorage --> MemoryCache
    EmbeddingCache --> DTCCache
    DTCCache --> ResponseCache
```

## 🚀 Deployment Architecture

### Development Environment
```mermaid
graph TB
    subgraph "Development Stack"
        React[React Dev Server]
        FastAPI[FastAPI Dev Server]
        Ollama[Ollama Service]
        Browser[Browser]
    end
    
    Browser --> React
    React --> FastAPI
    FastAPI --> Ollama
    FastAPI --> Browser
```

## 📋 Architecture Decisions

### Technology Choices
- **Frontend**: React + TypeScript for type safety and modern development
- **Backend**: FastAPI for high performance and automatic API documentation
- **AI**: Ollama for local LLM processing without external dependencies
- **Vector Search**: Sentence-transformers for semantic search capabilities
- **Data Processing**: PyMuPDF for secure PDF image extraction

### Security Decisions
- **Local Processing**: All AI operations performed locally
- **Memory-Only**: Confidential images processed in RAM only
- **No External APIs**: No sensitive data sent to external services
- **Input Validation**: Comprehensive validation and sanitization

### Performance Decisions
- **Caching**: Local caching for embeddings and DTC data
- **Lazy Loading**: Images and data loaded on demand
- **Optimized Queries**: Efficient search algorithms
- **Responsive Design**: Optimized for various screen sizes 