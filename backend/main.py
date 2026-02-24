from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Import services
from services.rag_service import rag_service
from config import settings

app = FastAPI(
    title="Physical AI Textbook Chatbot API",
    description="RAG chatbot for Physical AI & Humanoid Robotics textbook",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    question: str
    selected_text: Optional[str] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    conversation_id: str
    search_results: Optional[List[Dict[str, Any]]] = None

class IngestRequest(BaseModel):
    document_text: str
    document_id: str
    metadata: Optional[dict] = None

class IngestResponse(BaseModel):
    success: bool
    chunks_processed: int
    document_id: str

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

class SearchResponse(BaseModel):
    results: List[dict]
    query: str

class SystemInfoResponse(BaseModel):
    qdrant_collection: Dict[str, Any]
    embedding_model: str
    llm_model: str
    chunk_size: int
    chunk_overlap: int

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Physical AI Textbook Chatbot API", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chatbot-api"}

@app.get("/system-info", response_model=SystemInfoResponse)
async def get_system_info():
    """Get system information and configuration."""
    try:
        system_info = rag_service.get_system_info()
        return SystemInfoResponse(**system_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system info: {str(e)}")

# Chat endpoint with RAG
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat question with RAG."""
    try:
        result = rag_service.generate_answer(
            question=request.question,
            selected_text=request.selected_text,
            conversation_history=None  # Could be retrieved from database
        )

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            conversation_id=request.conversation_id or str(uuid.uuid4()),
            search_results=result.get("search_results", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

# Ingest endpoint
@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest):
    """Ingest document text into the RAG system."""
    try:
        result = rag_service.ingest_document(
            document_text=request.document_text,
            document_id=request.document_id,
            metadata=request.metadata
        )

        return IngestResponse(
            success=result["success"],
            chunks_processed=result["chunks_processed"],
            document_id=result["document_id"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")

# Search endpoint
@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search documents without generating a response."""
    try:
        results = rag_service.search_documents(
            query=request.query,
            limit=request.limit
        )

        return SearchResponse(
            results=results,
            query=request.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

# Selected text endpoint
@app.post("/selected-text")
async def process_selected_text(request: ChatRequest):
    """Process question with selected text as context."""
    try:
        if not request.selected_text:
            raise HTTPException(status_code=400, detail="No selected text provided")

        result = rag_service.generate_answer(
            question=request.question,
            selected_text=request.selected_text
        )

        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "context_used": result.get("context_used", ""),
            "conversation_id": request.conversation_id or str(uuid.uuid4())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing selected text: {str(e)}")

# Initialize with sample data if needed
@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup."""
    print("Starting up Physical AI Textbook Chatbot API...")

    # Check if OpenAI API key is configured
    if not settings.openai_api_key:
        print("WARNING: OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")

    # Check if Qdrant is accessible
    try:
        info = rag_service.get_system_info()
        print(f"Qdrant collection info: {info['qdrant_collection']}")
    except Exception as e:
        print(f"WARNING: Could not connect to Qdrant: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)