# 🚀 DiaNav Startup Guide

## Quick Start

### Option 1: One-Click Start (Recommended)
```bash
# Double-click this file or run in PowerShell:
.\start_dianav.bat
```

### Option 2: PowerShell Script
```bash
# Run the PowerShell script directly:
.\start_dianav.ps1
```

### Option 3: Manual Start
```bash
# Start backend:
python dianav_backend.py

# In another terminal, start frontend:
cd dianav-frontend
npm start
```

## Stop Servers

### Quick Stop
```bash
# Stop all DiaNav servers:
.\stop_dianav.ps1
```

## What the Startup Script Does

✅ **Automatically checks for existing processes** and stops them  
✅ **Starts the FastAPI backend** on port 8000  
✅ **Starts the React frontend** on port 3000  
✅ **Monitors server status** and shows real-time updates  
✅ **Opens the application** in your browser automatically  

## Access Points

- **🌐 Frontend App**: http://localhost:3000
- **📊 Backend API**: http://localhost:8000
- **📖 API Health**: http://localhost:8000/health

## Test the System

Once both servers are running, try asking:
- "What is DTC B1087?"
- "How do I troubleshoot LIN bus off error?"
- "Tell me all symptoms for B1087."

## Troubleshooting

### Port Already in Use
The startup script automatically handles this by killing existing processes.

### Frontend Won't Start
Make sure you have Node.js installed and run:
```bash
cd dianav-frontend
npm install
npm start
```

### Backend Won't Start
Make sure you have Python dependencies installed:
```bash
pip install -r requirements.txt
```

## Features

🎯 **Improved Image Extraction**: Now filters out logos, headers, and footers  
🔒 **Secure Processing**: All images processed in memory only  
🤖 **AI-Ready**: Prepared for Ollama LLM integration  
📱 **Professional UI**: Modern, responsive interface  
🔍 **Smart Search**: Advanced DTC code pattern matching 