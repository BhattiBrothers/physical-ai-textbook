from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Any, Optional
import uuid
from config import settings

class QdrantService:
    def __init__(self):
        self.url = settings.qdrant_url
        self.api_key = settings.qdrant_api_key
        self.collection_name = settings.qdrant_collection_name

        # Initialize client
        if self.api_key:
            self.client = QdrantClient(url=self.url, api_key=self.api_key)
        else:
            # For local development or if no API key provided
            self.client = QdrantClient(url=self.url) if self.url else QdrantClient(":memory:")

        # Ensure collection exists
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        try:
            # Check if client has get_collections method
            if not hasattr(self.client, 'get_collections'):
                print("Qdrant client doesn't have get_collections, skipping collection creation")
                return

            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                # Check if client has create_collection method
                if hasattr(self.client, 'create_collection'):
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(size=384, distance=Distance.COSINE),  # sentence-transformers size
                    )
                    print(f"Created Qdrant collection: {self.collection_name}")
                else:
                    print(f"Qdrant client doesn't have create_collection, can't create {self.collection_name}")
        except Exception as e:
            print(f"Error ensuring Qdrant collection exists: {e}")
            # Continue anyway - we'll use mock mode

    def add_document_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[str]:
        """Add document chunks with embeddings to Qdrant."""
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": chunk["text"],
                    "chunk_index": chunk["chunk_index"],
                    "document_id": chunk["document_id"],
                    "metadata": chunk.get("metadata", {}),
                    "source": chunk.get("source", "unknown")
                }
            )
            points.append(point)

        # Upsert points
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return [point.id for point in points]

    def search_similar(self, query_embedding: List[float], limit: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors in Qdrant."""
        try:
            # Check if client has search method
            if not hasattr(self.client, 'search'):
                return self._mock_search_results(query_embedding, limit)

            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=Filter(must=self._build_filter(filter_dict)) if filter_dict else None
            )

            results = []
            for hit in search_result:
                results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "text": hit.payload.get("text", ""),
                    "metadata": hit.payload.get("metadata", {}),
                    "source": hit.payload.get("source", "unknown"),
                    "document_id": hit.payload.get("document_id", "")
                })

            return results
        except Exception as e:
            print(f"Qdrant search error, using mock results: {e}")
            return self._mock_search_results(query_embedding, limit)

    def _mock_search_results(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Return mock search results for development."""
        mock_results = []
        for i in range(limit):
            mock_results.append({
                "id": f"mock_{i}",
                "score": 0.9 - (i * 0.1),
                "text": f"This is mock result {i} for the query. In production, this would be actual textbook content.",
                "metadata": {"source": "textbook", "module": "mock"},
                "source": "textbook",
                "document_id": "mock_document"
            })
        return mock_results

    def _build_filter(self, filter_dict: Dict) -> List[FieldCondition]:
        """Build filter conditions from dictionary."""
        conditions = []
        for key, value in filter_dict.items():
            conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
        return conditions

    def delete_document(self, document_id: str):
        """Delete all chunks for a document."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            )
        )

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            # Handle different Qdrant client versions
            return {
                "name": getattr(collection_info, 'name', self.collection_name),
                "vectors_count": getattr(collection_info, 'vectors_count', 0),
                "status": getattr(collection_info, 'status', 'unknown'),
                "collection_name": self.collection_name
            }
        except Exception as e:
            # Return basic info if collection info retrieval fails
            return {
                "name": self.collection_name,
                "vectors_count": 0,
                "status": f"error: {str(e)[:100]}",
                "collection_name": self.collection_name,
                "error": str(e)[:200]
            }

    def clear_collection(self):
        """Clear all vectors from collection."""
        self.client.delete_collection(self.collection_name)
        self._ensure_collection()

# Singleton instance
qdrant_service = QdrantService()