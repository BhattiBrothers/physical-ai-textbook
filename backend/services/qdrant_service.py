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
        collections = self.client.get_collections()
        collection_names = [col.name for col in collections.collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),  # OpenAI embedding size
            )

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
        collection_info = self.client.get_collection(self.collection_name)
        return {
            "name": collection_info.name,
            "vectors_count": collection_info.vectors_count,
            "status": collection_info.status
        }

    def clear_collection(self):
        """Clear all vectors from collection."""
        self.client.delete_collection(self.collection_name)
        self._ensure_collection()

# Singleton instance
qdrant_service = QdrantService()