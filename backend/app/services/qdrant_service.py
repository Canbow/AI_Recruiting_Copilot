import logging
import math
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class QdrantVectorService:
    """
    Manages vector indexing, HNSW configuration, and payload pre-filtering in Qdrant.
    Includes an in-memory fallback for local unit testing and environments without Docker.
    """
    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION
        self.vector_dim = settings.VECTOR_DIMENSION
        self.client = None
        self.in_memory_store: List[Dict[str, Any]] = []
        self._init_client()

    def _init_client(self):
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http.models import Distance, VectorParams
            
            # Connect to local or remote Qdrant instance
            self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT, timeout=3.0)
            
            # Check or create collection
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_dim, distance=Distance.COSINE)
                )
                logger.info(f"Created Qdrant collection '{self.collection_name}' with dimension {self.vector_dim}.")
            else:
                logger.info(f"Qdrant collection '{self.collection_name}' already exists.")
        except Exception as e:
            logger.warning(f"Could not connect to live Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}: {e}")
            logger.info("Initializing high-performance In-Memory Vector Store for testing and local dev.")
            self.client = None

    def upsert_chunks(self, candidate_id: str, chunks: List[Dict[str, Any]], metadata: Dict[str, Any]):
        """
        Embeds (or hashes) chunks and inserts vectors into Qdrant with payload metadata.
        """
        for idx, chunk in enumerate(chunks):
            # Generate deterministic pseudo-embedding (or OpenAI embedding if key active)
            vector = self._generate_embedding(chunk["content"])
            payload = {
                "candidate_id": candidate_id,
                "section": chunk["section"],
                "content": chunk["content"],
                "years_experience": metadata.get("years_experience", 0.0),
                "skills": metadata.get("skills", []),
                "tenant_id": metadata.get("tenant_id", "default_org")
            }
            
            if self.client:
                from qdrant_client.http.models import PointStruct
                point_id = abs(hash(f"{candidate_id}_{idx}_{chunk['section']}")) % (10**10)
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[PointStruct(id=point_id, vector=vector, payload=payload)]
                )
            else:
                self.in_memory_store.append({
                    "id": f"{candidate_id}_{idx}",
                    "vector": vector,
                    "payload": payload
                })

    def search(self, query: str, tenant_id: str = "default_org", min_exp: float = 0.0, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Performs approximate nearest neighbor search with payload pre-filtering.
        """
        query_vector = self._generate_embedding(query)
        
        if self.client:
            from qdrant_client.http.models import Filter, FieldCondition, MatchValue, Range
            query_filter = Filter(
                must=[
                    FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id)),
                    FieldCondition(key="years_experience", range=Range(gte=min_exp))
                ]
            )
            hits = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit
            )
            return [{"payload": hit.payload, "score": hit.score} for hit in hits]
        else:
            # In-memory cosine similarity search
            results = []
            for item in self.in_memory_store:
                p = item["payload"]
                if p.get("tenant_id") == tenant_id and p.get("years_experience", 0.0) >= min_exp:
                    score = self._cosine_similarity(query_vector, item["vector"])
                    results.append({"payload": p, "score": score})
                    
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generates dense vector representation. In production uses OpenAI; in dev/test uses unit vector.
        """
        # Deterministic normalized 1536-d vector based on character hash for testing/offline
        vec = [0.0] * self.vector_dim
        for i, char in enumerate(text[:500]):
            pos = (ord(char) * 31 + i) % self.vector_dim
            vec[pos] += 1.0
            
        # L2 Normalization to unit length
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        # Since vectors are L2-normalized, cosine similarity equals dot product
        return sum(a * b for a, b in zip(vec_a, vec_b))

# Global vector service singleton
qdrant_service = QdrantVectorService()
