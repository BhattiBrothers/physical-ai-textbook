from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

from services.rag_service import rag_service
from services.ingest_textbook import ingest_all
from routers import auth, translation, personalization
from models import create_tables
from config import settings

app = FastAPI(
    title="Physical AI Textbook Chatbot API",
    description="RAG chatbot for Physical AI & Humanoid Robotics textbook",
    version="1.0.0"
)

# CORS — allow_credentials MUST be False when allow_origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Explicit OPTIONS handler — belt-and-suspenders for preflight requests
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept",
            "Access-Control-Max-Age": "3600",
        },
    )

# Include routers
app.include_router(auth.router)
app.include_router(translation.router)
app.include_router(personalization.router)

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

@app.get("/")
async def root():
    return {"message": "Physical AI Textbook Chatbot API", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chatbot-api"}

@app.get("/system-info", response_model=SystemInfoResponse)
async def get_system_info():
    try:
        system_info = rag_service.get_system_info()
        return SystemInfoResponse(**system_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system info: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = rag_service.generate_answer(
            question=request.question,
            selected_text=request.selected_text,
            conversation_history=None
        )
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            conversation_id=request.conversation_id or str(uuid.uuid4()),
            search_results=result.get("search_results", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest):
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

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    try:
        results = rag_service.search_documents(query=request.query, limit=request.limit)
        return SearchResponse(results=results, query=request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@app.post("/selected-text")
async def process_selected_text(request: ChatRequest):
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

@app.on_event("startup")
async def startup_event():
    print("Starting Physical AI Textbook Chatbot API...")
    create_tables()
    print("Database tables ready")
    try:
        ingest_all(rag_service)
    except Exception as e:
        print(f"WARNING: Textbook ingestion failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
