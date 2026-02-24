from typing import List, Dict, Any
import tiktoken
from config import settings
from services.openai_service import openai_service

class EmbeddingService:
    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split text into chunks with overlapping windows."""
        # Tokenize the text
        tokens = self.tokenizer.encode(text)

        chunks = []
        start = 0

        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)

            # Create chunk dictionary
            chunk = {
                "text": chunk_text,
                "chunk_index": len(chunks),
                "token_count": len(chunk_tokens),
                "metadata": metadata or {}
            }

            chunks.append(chunk)

            # Move start position, accounting for overlap
            start += self.chunk_size - self.chunk_overlap

        return chunks

    def chunk_document(self, document_text: str, document_id: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Chunk a document and add document metadata."""
        base_metadata = {
            "document_id": document_id,
            "source": "textbook",
            **metadata if metadata else {}
        }

        chunks = self.chunk_text(document_text, base_metadata)

        # Add document-specific metadata to each chunk
        for i, chunk in enumerate(chunks):
            chunk["document_id"] = document_id
            chunk["chunk_index"] = i
            if "metadata" not in chunk:
                chunk["metadata"] = {}
            chunk["metadata"].update(base_metadata)

        return chunks

    def create_embeddings_for_chunks(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """Create embeddings for a list of text chunks."""
        texts = [chunk["text"] for chunk in chunks]

        try:
            # Use OpenAI embeddings
            embeddings = openai_service.create_embeddings_batch(texts)
            return embeddings
        except Exception as e:
            # Fallback to sentence transformers if OpenAI fails
            print(f"OpenAI embedding failed, using fallback: {e}")
            return self._create_fallback_embeddings(texts)

    def _create_fallback_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Fallback embedding method using sentence-transformers."""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            embeddings = model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            # Last resort: return random embeddings (not for production)
            import numpy as np
            print(f"Fallback embedding also failed: {e}")
            return [np.random.randn(384).tolist() for _ in texts]

    def prepare_document_for_ingestion(self, document_text: str, document_id: str, metadata: Dict[str, Any] = None) -> tuple[List[Dict[str, Any]], List[List[float]]]:
        """Prepare document for ingestion by chunking and creating embeddings."""
        chunks = self.chunk_document(document_text, document_id, metadata)
        embeddings = self.create_embeddings_for_chunks(chunks)

        # Ensure we have the same number of chunks and embeddings
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch between chunks ({len(chunks)}) and embeddings ({len(embeddings)})")

        return chunks, embeddings

# Singleton instance
embedding_service = EmbeddingService()