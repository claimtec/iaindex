"""
Semantic Query Service

Provides semantic search over embedded content using vector similarity.
Only available for verified publishers with analytics tracking.
"""
import logging
import hashlib
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field

# Lazy imports for optional dependencies
if TYPE_CHECKING:
    import pinecone
    from weaviate import Client as WeaviateClient
    import numpy as np

from .embeddings import EmbeddingsService, EmbeddingsConfig, VectorStore

logger = logging.getLogger(__name__)


# Models
class SemanticQueryRequest(BaseModel):
    """Request for semantic search"""
    q: str = Field(..., description="Search query", min_length=1, max_length=500)
    domain: str = Field(..., description="Domain to search within")
    top_k: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of results to return"
    )
    min_score: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score (0-1)"
    )
    vector_store: VectorStore = Field(
        default="pinecone",
        description="Vector store to query"
    )
    namespace: Optional[str] = Field(
        default=None,
        description="Namespace to search in"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata filters"
    )


class SearchResult(BaseModel):
    """Single search result"""
    page_url: str
    title: str
    score: float
    snippet: str
    chunk_id: str
    chunk_index: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SemanticQueryResponse(BaseModel):
    """Response from semantic search"""
    query: str
    domain: str
    results: List[SearchResult]
    total_results: int
    query_time_ms: float
    timestamp: datetime


class QueryAnalytics(BaseModel):
    """Analytics data for a query"""
    query_id: str
    query: str
    domain: str
    result_count: int
    top_score: Optional[float] = None
    query_time_ms: float
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None


# Exceptions
class SemanticQueryError(Exception):
    """Base exception for semantic query errors"""
    pass


class UnverifiedPublisherError(SemanticQueryError):
    """Publisher not verified"""
    pass


class VectorStoreQueryError(SemanticQueryError):
    """Vector store query error"""
    pass


class SemanticQueryService:
    """
    Service for semantic search over embedded content

    Features:
    - Vector similarity search
    - Publisher verification check
    - Query analytics tracking
    - Multiple vector store support
    - Metadata filtering
    """

    def __init__(self):
        """Initialize semantic query service"""
        self.config = EmbeddingsConfig()
        self.embeddings_service = EmbeddingsService()

        # Vector store clients
        self.pinecone_index = None
        self.weaviate_client = None

        # Analytics storage (in-memory for demo)
        self.analytics_buffer: List[QueryAnalytics] = []

    def _init_pinecone(self):
        """Initialize Pinecone client"""
        if self.pinecone_index is None:
            try:
                import pinecone
                pinecone.init(
                    api_key=self.config.PINECONE_API_KEY,
                    environment=self.config.PINECONE_ENVIRONMENT
                )
                self.pinecone_index = pinecone.Index(self.config.PINECONE_INDEX_NAME)
                logger.info(f"Connected to Pinecone index: {self.config.PINECONE_INDEX_NAME}")
            except ImportError as e:
                logger.error(f"pinecone library not installed: {e}")
                raise VectorStoreQueryError("pinecone library is required for Pinecone vector store")
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone: {e}")
                raise VectorStoreQueryError(f"Failed to initialize Pinecone: {str(e)}")

    def _init_weaviate(self):
        """Initialize Weaviate client"""
        if self.weaviate_client is None:
            try:
                from weaviate import Client as WeaviateClient
                auth_config = None
                if self.config.WEAVIATE_API_KEY:
                    from weaviate.auth import AuthApiKey
                    auth_config = AuthApiKey(api_key=self.config.WEAVIATE_API_KEY)

                self.weaviate_client = WeaviateClient(
                    url=self.config.WEAVIATE_URL,
                    auth_client_secret=auth_config
                )
                logger.info(f"Connected to Weaviate at {self.config.WEAVIATE_URL}")
            except ImportError as e:
                logger.error(f"weaviate library not installed: {e}")
                raise VectorStoreQueryError("weaviate library is required for Weaviate vector store")
            except Exception as e:
                logger.error(f"Failed to initialize Weaviate: {e}")
                raise VectorStoreQueryError(f"Failed to initialize Weaviate: {str(e)}")

    async def verify_publisher(self, domain: str) -> bool:
        """
        Verify that publisher domain is verified

        Args:
            domain: Domain to verify

        Returns:
            True if verified

        Raises:
            UnverifiedPublisherError: If publisher not verified
        """
        # TODO: Implement actual verification check against database
        # For now, we'll assume all domains are verified
        # In production, check against Supabase publishers table

        logger.info(f"Checking verification status for domain: {domain}")

        # Placeholder verification logic
        # This should query your publishers table:
        # SELECT verified_at FROM publishers WHERE domain = domain AND verified_at IS NOT NULL

        verified = True  # Placeholder

        if not verified:
            raise UnverifiedPublisherError(f"Domain {domain} is not verified")

        return True

    def _generate_query_id(self, query: str, domain: str, timestamp: datetime) -> str:
        """
        Generate unique query ID

        Args:
            query: Search query
            domain: Domain
            timestamp: Query timestamp

        Returns:
            Unique query ID
        """
        content = f"{query}:{domain}:{timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _extract_snippet(self, text: str, max_length: int = 200) -> str:
        """
        Extract snippet from text

        Args:
            text: Full text
            max_length: Maximum snippet length

        Returns:
            Snippet with ellipsis if truncated
        """
        if len(text) <= max_length:
            return text

        # Try to break at sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        if last_period > max_length * 0.7:  # If period is in last 30%
            return truncated[:last_period + 1]

        return truncated + "..."

    async def query_pinecone(
        self,
        query_vector: List[float],
        domain: str,
        top_k: int,
        min_score: float,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query Pinecone for similar vectors

        Args:
            query_vector: Query embedding vector
            domain: Domain to filter by
            top_k: Number of results
            min_score: Minimum similarity score
            namespace: Optional namespace
            filters: Additional metadata filters

        Returns:
            List of matching results

        Raises:
            VectorStoreQueryError: If query fails
        """
        self._init_pinecone()

        try:
            # Build filter
            query_filter = {"page_url": {"$regex": f"^https?://{domain}"}}
            if filters:
                query_filter.update(filters)

            # Query Pinecone
            results = self.pinecone_index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace or "",
                filter=query_filter,
                include_metadata=True
            )

            # Filter by minimum score
            matches = [
                match for match in results.matches
                if match.score >= min_score
            ]

            logger.info(
                f"Pinecone query returned {len(matches)} results "
                f"(from {len(results.matches)} total)"
            )

            return matches

        except Exception as e:
            logger.error(f"Error querying Pinecone: {e}")
            raise VectorStoreQueryError(f"Pinecone query failed: {str(e)}")

    async def query_weaviate(
        self,
        query_vector: List[float],
        domain: str,
        top_k: int,
        min_score: float,
        namespace: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query Weaviate for similar vectors

        Args:
            query_vector: Query embedding vector
            domain: Domain to filter by
            top_k: Number of results
            min_score: Minimum similarity score
            namespace: Optional namespace
            filters: Additional metadata filters

        Returns:
            List of matching results

        Raises:
            VectorStoreQueryError: If query fails
        """
        self._init_weaviate()

        try:
            # Build where filter
            where_filter = {
                "path": ["page_url"],
                "operator": "Like",
                "valueText": f"*{domain}*"
            }

            if namespace:
                where_filter = {
                    "operator": "And",
                    "operands": [
                        where_filter,
                        {
                            "path": ["namespace"],
                            "operator": "Equal",
                            "valueText": namespace
                        }
                    ]
                }

            # Query Weaviate
            results = (
                self.weaviate_client.query
                .get(self.config.WEAVIATE_CLASS_NAME, [
                    "chunk_id",
                    "page_url",
                    "page_title",
                    "chunk_index",
                    "text",
                    "created_at"
                ])
                .with_near_vector({"vector": query_vector})
                .with_where(where_filter)
                .with_limit(top_k)
                .with_additional(["distance", "certainty"])
                .do()
            )

            objects = results.get("data", {}).get("Get", {}).get(
                self.config.WEAVIATE_CLASS_NAME, []
            )

            # Filter by minimum score (certainty)
            matches = [
                obj for obj in objects
                if obj.get("_additional", {}).get("certainty", 0) >= min_score
            ]

            logger.info(
                f"Weaviate query returned {len(matches)} results "
                f"(from {len(objects)} total)"
            )

            return matches

        except Exception as e:
            logger.error(f"Error querying Weaviate: {e}")
            raise VectorStoreQueryError(f"Weaviate query failed: {str(e)}")

    async def semantic_query(
        self,
        request: SemanticQueryRequest,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> SemanticQueryResponse:
        """
        Perform semantic search

        Args:
            request: Query request
            user_id: Optional user ID for analytics
            session_id: Optional session ID for analytics

        Returns:
            Query response

        Raises:
            SemanticQueryError: If query fails
        """
        start_time = datetime.utcnow()

        # Step 1: Verify publisher
        await self.verify_publisher(request.domain)

        # Step 2: Generate query embedding
        logger.info(f"Generating embedding for query: {request.q}")

        # Determine which model to use based on vector store configuration
        # For simplicity, we'll use the model that matches the stored vectors
        # In production, this should be stored in the embeddings manifest

        # Try OpenAI first, fall back to local model
        try:
            query_vectors = await self.embeddings_service.generate_embeddings_openai(
                [request.q]
            )
            query_vector = query_vectors[0]
        except Exception as e:
            logger.warning(f"OpenAI embedding failed, using local model: {e}")
            query_vectors = self.embeddings_service.generate_embeddings_local(
                [request.q]
            )
            query_vector = query_vectors[0]

        # Step 3: Query vector store
        if request.vector_store == "pinecone":
            matches = await self.query_pinecone(
                query_vector=query_vector,
                domain=request.domain,
                top_k=request.top_k,
                min_score=request.min_score,
                namespace=request.namespace,
                filters=request.filters
            )

            # Convert Pinecone results to SearchResult
            search_results = []
            for match in matches:
                metadata = match.metadata
                search_results.append(SearchResult(
                    page_url=metadata.get("page_url", ""),
                    title=metadata.get("page_title", ""),
                    score=float(match.score),
                    snippet=self._extract_snippet(metadata.get("text", "")),
                    chunk_id=match.id,
                    chunk_index=metadata.get("chunk_index", 0),
                    metadata={
                        k: v for k, v in metadata.items()
                        if k not in ["page_url", "page_title", "text", "chunk_index"]
                    }
                ))

        else:  # weaviate
            matches = await self.query_weaviate(
                query_vector=query_vector,
                domain=request.domain,
                top_k=request.top_k,
                min_score=request.min_score,
                namespace=request.namespace,
                filters=request.filters
            )

            # Convert Weaviate results to SearchResult
            search_results = []
            for match in matches:
                search_results.append(SearchResult(
                    page_url=match.get("page_url", ""),
                    title=match.get("page_title", ""),
                    score=float(match.get("_additional", {}).get("certainty", 0)),
                    snippet=self._extract_snippet(match.get("text", "")),
                    chunk_id=match.get("chunk_id", ""),
                    chunk_index=match.get("chunk_index", 0),
                    metadata={}
                ))

        # Calculate query time
        query_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Step 4: Track analytics
        query_id = self._generate_query_id(request.q, request.domain, start_time)
        analytics = QueryAnalytics(
            query_id=query_id,
            query=request.q,
            domain=request.domain,
            result_count=len(search_results),
            top_score=search_results[0].score if search_results else None,
            query_time_ms=query_time_ms,
            timestamp=start_time,
            user_id=user_id,
            session_id=session_id
        )
        self.analytics_buffer.append(analytics)

        # Flush analytics if buffer is full
        if len(self.analytics_buffer) >= 100:
            await self.flush_analytics()

        logger.info(
            f"Semantic query completed: {len(search_results)} results "
            f"in {query_time_ms:.2f}ms"
        )

        return SemanticQueryResponse(
            query=request.q,
            domain=request.domain,
            results=search_results,
            total_results=len(search_results),
            query_time_ms=query_time_ms,
            timestamp=start_time
        )

    async def flush_analytics(self):
        """Flush analytics buffer to storage"""
        if not self.analytics_buffer:
            return

        logger.info(f"Flushing {len(self.analytics_buffer)} analytics records")

        # TODO: Store analytics in database
        # This should write to a query_analytics table with fields:
        # - query_id, query, domain, result_count, top_score
        # - query_time_ms, timestamp, user_id, session_id

        # For now, just log
        for analytics in self.analytics_buffer:
            logger.debug(f"Analytics: {analytics.dict()}")

        self.analytics_buffer.clear()

    async def get_query_analytics(
        self,
        domain: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get query analytics for a domain

        Args:
            domain: Domain to get analytics for
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Analytics data
        """
        # Filter analytics by domain and date range
        filtered = [
            a for a in self.analytics_buffer
            if a.domain == domain
            and (not start_date or a.timestamp >= start_date)
            and (not end_date or a.timestamp <= end_date)
        ]

        total_queries = len(filtered)
        if total_queries == 0:
            return {
                "domain": domain,
                "total_queries": 0,
                "avg_results": 0,
                "avg_query_time_ms": 0,
                "avg_top_score": 0
            }

        avg_results = sum(a.result_count for a in filtered) / total_queries
        avg_query_time = sum(a.query_time_ms for a in filtered) / total_queries
        scores = [a.top_score for a in filtered if a.top_score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "domain": domain,
            "total_queries": total_queries,
            "avg_results": avg_results,
            "avg_query_time_ms": avg_query_time,
            "avg_top_score": avg_score,
            "queries": [
                {
                    "query": a.query,
                    "result_count": a.result_count,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in filtered[-10:]  # Last 10 queries
            ]
        }


# Singleton instance
_semantic_query_service: Optional[SemanticQueryService] = None


def get_semantic_query_service() -> SemanticQueryService:
    """Get or create semantic query service instance"""
    global _semantic_query_service
    if _semantic_query_service is None:
        _semantic_query_service = SemanticQueryService()
    return _semantic_query_service
