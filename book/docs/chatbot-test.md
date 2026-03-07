---
title: Chatbot Test Page
description: Test page for the Physical AI Textbook Chatbot
sidebar_position: 100
---

# 🤖 Chatbot Test Page

This page demonstrates the integrated RAG chatbot for the Physical AI textbook.

## Chatbot Component

The chatbot component is integrated below. You can:

1. **Type questions** in the input field
2. **Select text** on any page and ask about it
3. **Get answers** based on textbook content

---

## Live Chatbot Demo

import ChatbotWidget from '@site/src/components/ChatbotWidget';

<ChatbotWidget />

---

## How the Chatbot Works

### 1. **RAG (Retrieval-Augmented Generation)**
- Searches textbook content for relevant information
- Uses vector embeddings and semantic search
- Combines retrieved context with AI generation

### 2. **Selected Text Detection**
- Select any text on the page
- Chatbot automatically detects your selection
- Ask questions specifically about the selected text

### 3. **Backend Integration**
- FastAPI backend at `http://localhost:8000`
- OpenAI GPT models for generation
- Qdrant vector database for document search

### 4. **Technical Features**
- **Context-aware responses** based on textbook content
- **Source citations** showing where information came from
- **Conversation memory** across multiple questions
- **Error handling** with fallback responses

---

## Testing Instructions

### Prerequisites
1. **Backend server running**: `cd backend && python main.py`
2. **Docusaurus dev server**: `cd book && npm start`
3. **Open this page**: `http://localhost:3000/physical-ai-textbook/docs/chatbot-test`

### Test Cases
1. **Basic questions**: "What is ROS 2?"
2. **Context-specific**: Select text about Gazebo and ask "How does this work?"
3. **Follow-up questions**: Ask follow-up questions based on previous answers
4. **Error handling**: Try asking unrelated questions

---

## Integration in Other Pages

To add the chatbot to any markdown page:

```jsx
import ChatbotWidget from '@site/src/components/ChatbotWidget';

<ChatbotWidget />
```

Or with custom height:
```jsx
<ChatbotWidget height="400px" />
```

---

## Troubleshooting

### Chatbot not responding?
1. Check if backend server is running: `http://localhost:8000`
2. Verify CORS is configured in backend
3. Check browser console for errors (F12 → Console)

### Selected text not detected?
1. Ensure you're selecting text on the page
2. Selection must be at least 3 characters
3. Works with text in markdown content areas

### Getting "Mock response"?
- Backend is running in mock mode (no OpenAI API key)
- Configure `OPENAI_API_KEY` in `.env` file for real responses

---

## Backend API Endpoints

- `POST /chat` - Main chat endpoint
- `POST /selected-text` - Process selected text
- `POST /search` - Search documents
- `POST /ingest` - Ingest new documents
- `GET /health` - Health check

---

## Development Status

✅ **Complete Features:**
- React chatbot component
- Selected text detection
- Mock backend for development
- API integration ready

🔄 **In Progress:**
- Production API key configuration
- Frontend-backend integration testing
- Performance optimization

---

*This chatbot enhances the learning experience by providing instant, contextual answers based on the Physical AI textbook content.*