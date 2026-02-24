# Physical AI Textbook Chatbot Backend

FastAPI backend for the Physical AI & Humanoid Robotics textbook RAG chatbot.

## Features

- **RAG Pipeline**: Retrieval-Augmented Generation using OpenAI, Qdrant, and document chunking
- **Document Ingestion**: Process textbook content into searchable vector embeddings
- **Semantic Search**: Find relevant textbook content for questions
- **Context-Aware Responses**: Generate answers based on retrieved context
- **Selected Text Support**: Answer questions about specific selected text passages

## Architecture

```
Frontend (Docusaurus) → FastAPI Backend → OpenAI API → Qdrant Vector DB → Neon Postgres
```

## API Endpoints

- `GET /`, `GET /health` - Health checks
- `GET /system-info` - System configuration info
- `POST /chat` - Main chat endpoint with RAG
- `POST /ingest` - Ingest document text
- `POST /search` - Semantic search without generation
- `POST /selected-text` - Answer based on selected text

## Setup

### 1. Prerequisites

- Python 3.10+
- Virtual environment
- OpenAI API key
- Qdrant instance (cloud or local)

### 2. Installation

```bash
# Clone the repository
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Copy `.env.example` to `.env` and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env` file:
- Set `OPENAI_API_KEY` with your OpenAI API key
- Configure `QDRANT_URL` and `QDRANT_API_KEY` for Qdrant
- Set `DATABASE_URL` for Neon Postgres (optional for development)

### 4. Running the Server

```bash
# Development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

### 5. API Documentation

Once running, visit:
- `http://localhost:8000/docs` - Interactive Swagger UI
- `http://localhost:8000/redoc` - ReDoc documentation

## Development

### Project Structure

```
backend/
├── main.py              # FastAPI application
├── config.py           # Configuration settings
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
├── services/          # Business logic services
│   ├── openai_service.py
│   ├── qdrant_service.py
│   ├── embedding_service.py
│   └── rag_service.py
└── README.md
```

### Ingesting Textbook Content

To ingest the textbook content into the RAG system:

```python
import requests

# Example: Ingest a chapter
response = requests.post("http://localhost:8000/ingest", json={
    "document_text": "Your chapter content here...",
    "document_id": "module-1-chapter-1",
    "metadata": {
        "module": "ROS 2",
        "chapter": "Introduction to ROS 2",
        "week": 1
    }
})
```

### Testing the Chatbot

```python
import requests

# Test chat endpoint
response = requests.post("http://localhost:8000/chat", json={
    "question": "What is ROS 2?",
    "conversation_id": "test-conversation"
})

print(response.json())
```

## Deployment

### Render.com

1. Create new Web Service
2. Connect GitHub repository
3. Set environment variables
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Railway.app

1. New Project → Deploy from GitHub
2. Add environment variables
3. Automatically detects Python and requirements.txt

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model for chat | `gpt-4-turbo-preview` |
| `OPENAI_EMBEDDING_MODEL` | OpenAI embedding model | `text-embedding-3-small` |
| `QDRANT_URL` | Qdrant instance URL | `:memory:` (in-memory) |
| `QDRANT_API_KEY` | Qdrant API key | Optional |
| `QDRANT_COLLECTION_NAME` | Qdrant collection name | `physical_ai_textbook` |
| `DATABASE_URL` | PostgreSQL connection URL | `sqlite:///./textbook.db` |
| `CHUNK_SIZE` | Text chunk size for embeddings | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap size | `200` |
| `MAX_TOKENS` | Maximum tokens for responses | `4000` |

## Troubleshooting

### OpenAI API Errors
- Ensure `OPENAI_API_KEY` is set correctly
- Check OpenAI account for sufficient credits

### Qdrant Connection Issues
- For local development, run Qdrant: `docker run -p 6333:6333 qdrant/qdrant`
- For cloud, verify URL and API key

### Database Connection
- Neon Postgres: Ensure connection string is correct
- Local SQLite: File will be created automatically

## License

Part of the Physical AI & Humanoid Robotics Textbook Hackathon Project.