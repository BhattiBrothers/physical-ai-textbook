from typing import List, Dict, Any, Optional
from services.openai_service import openai_service
from services.qdrant_service import qdrant_service
from services.embedding_service import embedding_service
import uuid
import services.ingest_textbook as textbook_store

class RAGService:
    def __init__(self):
        self.openai = openai_service
        self.qdrant = qdrant_service
        self.embedding = embedding_service

    def ingest_document(self, document_text: str, document_id: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ingest a document into the RAG system."""
        # Chunk and embed document
        chunks, embeddings = self.embedding.prepare_document_for_ingestion(
            document_text, document_id, metadata
        )

        # Store in Qdrant
        point_ids = self.qdrant.add_document_chunks(chunks, embeddings)

        return {
            "success": True,
            "document_id": document_id,
            "chunks_processed": len(chunks),
            "point_ids": point_ids
        }

    def retrieve_relevant_context(self, query: str, limit: int = 5, filter_dict: Optional[Dict] = None) -> tuple[str, List[Dict[str, Any]]]:
        """Retrieve relevant context for a query."""
        # Create query embedding
        query_embedding = self.openai.create_embedding(query)

        # Search for similar chunks
        results = self.qdrant.search_similar(query_embedding, limit, filter_dict)

        # Combine retrieved texts
        context_text = "\n\n".join([result["text"] for result in results])

        return context_text, results

    def generate_answer(self, question: str, selected_text: Optional[str] = None, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Generate answer using RAG pipeline."""
        if selected_text:
            context = selected_text
            sources = ["selected_text"]
            search_results = []
        else:
            try:
                context, search_results = self.retrieve_relevant_context(question)
                sources = list(set([r.get("source", "unknown") for r in search_results]))
            except Exception as e:
                print(f"Vector retrieval failed, using keyword search: {e}")
                context = ""
                search_results = []
                sources = []

            # If vector search returned nothing useful, try keyword fallback
            if not context or not context.strip() or "mock result" in context:
                context = textbook_store.keyword_search(question)
                sources = ["textbook-keyword-search"] if context else []
                print(f"Keyword fallback context length: {len(context)}")

        answer = self.openai.generate_rag_response(
            question=question,
            context=context,
            conversation_history=conversation_history
        )

        citation_info = self.openai.extract_citations(answer, sources)

        return {
            "answer": citation_info["answer"],
            "sources": citation_info["sources"],
            "citations": citation_info["citations"],
            "search_results": search_results,
            "context_used": context[:500] + "..." if len(context) > 500 else context
        }

    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search documents without generating an answer."""
        query_embedding = self.openai.create_embedding(query)
        results = self.qdrant.search_similar(query_embedding, limit)

        return results

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """Delete a document from the RAG system."""
        self.qdrant.delete_document(document_id)
        return {"success": True, "document_id": document_id}

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        collection_info = self.qdrant.get_collection_info()

        return {
            "qdrant_collection": collection_info,
            "embedding_model": self.openai.embedding_model,
            "llm_model": self.openai.model,
            "chunk_size": self.embedding.chunk_size,
            "chunk_overlap": self.embedding.chunk_overlap
        }

# Singleton instance
rag_service = RAGService()