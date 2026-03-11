# LLA - Legendary Legal Assistant

LLA is an AI-powered web application that automates the generation of legal documents, reducing the need for manual drafting by a lawyer.

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│   React Frontend (Vite)         │
│  - Document Editor              │
│  - File Browser                 │
│  - Chat Panel                   │            
└──────────────┬──────────────────┘
               │ WebSocket
               │ (ws://localhost:8000)
┌──────────────▼──────────────────┐
│   Python Backend (WebSockets)    │
│  - Document Processing           │
│  - LLM Integration               │
│  - JSON Generation               │
└─────────────────────────────────┘
```

## 📦 Tech Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **Mammoth** - DOCX text extraction

### Backend
- **Python 3.11+** - Runtime
- **Websockets** - Real-time communication
- **OpenAI/LiteLLM** - LLM integration
- **Asyncio** - Async runtime

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (Frontend)
- Python 3.11+ (Backend)
- OpenAI API key (for LLM)

### Installation

**1. Backend Setup**

```bash
cd /LLA/src/LLM

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
# Create .env file and add:
# LITELLM_API_KEY=your_api_key_here
# or
# OPENAI_API_KEY=your_openai_key_here
```

**2. Frontend Setup**

```bash
cd LLA/src/frontend

# Install Node dependencies
npm install

# or with bun:
# bun install
```

## 🎯 How to Use

### Starting the Application

**Terminal 1 - Backend:**
```bash
#run template creator
cd /LLA/src/LLM
python websocketService.py

#run edditor
cd /LLA/src/LLM
python websocketServiceEdditor.py
```

Expected output:
```
Starting websocket server on ws://localhost:8000
Websocket server is running on ws://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
#run template creator
cd /LLA/src/new_frontend
npm run dev

#run edditor
cd /LLA/src/frontend
npm run dev
```

Expected output:
```
  Local: http://localhost:8080/
```

**Version:** 1.0.0  
**Last Updated:** March 2026  
**Status:** Active Development
