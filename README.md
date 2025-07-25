# DiaNav: Diagnostic Navigator

DiaNav is an advanced AI-powered assistant for automotive diagnostics, designed to help engineers and technicians quickly understand, troubleshoot, and resolve vehicle issues using natural language queries. It leverages structured data from annotated PDF sources and provides both conversational and structured responses.

---

## 🚗 Project Overview

**DiaNav** enables users to:
- Query DTC codes, symptoms, fault conditions, and healing procedures in plain English.
- Receive both a human-like explanation and a structured output matching the original data format.
- Interact via a modern, professional web interface inspired by best-in-class AI chat UIs.
- Ingest and index structured `.txt` and `.json` data (extracted from OEM PDF manuals).

---

## 🛠️ Tech Stack
- **Frontend:** React, TypeScript, CSS (custom, Flexbox)
- **Backend:** FastAPI (Python), Pydantic, Uvicorn
- **AI/NLP:** OpenAI API (mocked for now, can be integrated)
- **Data:** Structured `.txt` and `.json` files (no OCR required)

---

## 📦 Features
- **Conversational UI:** Ask questions like "What causes B1087?" or "How do I troubleshoot LIN bus off error?"
- **Structured Output:** Always returns a block matching the original DTC data format.
- **Multi-chat Sessions:** Sidebar for managing multiple conversations (like ChatGPT).
- **Responsive Design:** Fits within a single browser window, with scrollable chat and collapsible sidebar.
- **Subtle Animations:** Professional, modern look and feel.

---

## 🚀 Getting Started

### 1. Clone the Repository
```sh
git clone https://github.com/meraxesism/DiaNav.git
cd DiaNav
```

### 2. Backend Setup
```sh
pip install -r requirements.txt
uvicorn dianav_backend:app --reload
```
- Make sure your structured `.txt` and `.json` data files are in the correct location (see `dianav_backend.py`).

### 3. Frontend Setup
```sh
cd dianav-frontend
npm install --legacy-peer-deps
npm start
```
- The frontend will be available at [http://localhost:3000](http://localhost:3000)

---

## 🧩 Project Structure
```
DiaNav/
├── dianav_backend.py         # FastAPI backend
├── dianav_data.py            # Data parsing logic
├── requirements.txt          # Python dependencies
├── dianav-frontend/
│   ├── src/
│   │   ├── App.tsx           # Main React app
│   │   ├── App.css           # Styles
│   │   └── ...
│   ├── package.json          # Frontend dependencies
│   └── ...
└── README.md                 # This file
```

---

## 📝 Usage Example
- **Query:** `What causes B1087?`
- **Conversational Response:**
  > Here is the information for DTC B1087. Please see the structured details below.
- **Structured Output:**
  > DTC_Code: B1087 ... (full block from .txt)

---

## 👤 Author & Contact
- **Owner:** meraxesism
- **For questions or collaboration:** Please open an issue or pull request on [GitHub](https://github.com/meraxesism/DiaNav)

---

## 📄 License
This project is for internal use and demonstration. Please contact the owner for licensing or external use inquiries. 