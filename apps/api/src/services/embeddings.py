"""
Vector Embeddings Service

Generates and manages vector embeddings for semantic search.
Supports OpenAI and local models, chunks text content, and stores vectors in Pinecone/Weaviate.
"""
import logging
import hashlib
import json
import os
from typing import List, Dict, Any, Optional, Literal, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
import httpx

# Lazy imports for optional dependencies
if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer
    import pinecone
    from weaviate import Client as WeaviateClient
    import numpy as np
    import tiktoken

logger = logging.getLogger(__name__)


# Configuration
class EmbeddingsConfig:
    """Configuration for embeddings service"""
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBEDDING_MODEL = "text-embedding-ada-002"
    OPENAI_API_URL = "https://api.openai.com/v1/embeddings"

    # Local models
    LOCAL_MODEL_NAME = "all-MiniLM-L6-v2"
    LOCAL_MODEL_DIMENSION = 384

    # Pinecone
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "iaindex-vectors")

    # Weaviate
    WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
    WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY", "")
    WEAVIATE_CLASS_NAME = "IAIndexPage"

    # Chunking settings
    MAX_CHUNK_TOKENS = 512
    CHUNK_OVERLAP = 50
    MIN_CHUNK_SIZE = 100

    # Rate limiting
    REQUEST_TIMEOUT = 30
    MAX_BATCH_SIZE = 100


# Models
EmbeddingModel = Literal["ada-002", "minilm"]
VectorStore = Literal["pinecone", "weaviate"]


class PageContent(BaseModel):
    """Page content for embedding"""
    url: HttpUrl
    title: str
    rendered_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BuildEmbeddingsRequest(BaseModel):
    """Request to build embeddings"""
    domain: str = Field(..., description="Domain to build embeddings for")
    pages: List[PageContent] = Field(..., description="Pages to embed")
    model: EmbeddingModel = Field(
        default="ada-002",
        description="Embedding model to use"
    )
    vector_store: VectorStore = Field(
        default="pinecone",
        description="Vector store to use"
    )
    namespace: Optional[str] = Field(
        default=None,
        description="Namespace for vector store"
    )


class BuildEmbeddingsResponse(BaseModel):
    """Response from building embeddings"""
    domain: str
    document_count: int
    chunk_count: int
    vector_count: int
    manifest_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class TextChunk(BaseModel):
    """A chunk of text with metadata"""
    chunk_id: str
    text: str
    page_url: str
    page_title: str
    chunk_index: int
    token_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EmbeddingVector(BaseModel):
    """Embedding vector with metadata"""
    chunk_id: str
    vector: List[float]
    chunk: TextChunk
    created_at: datetime


class EmbeddingsManifest(BaseModel):
    """Manifest for embeddings collection"""
    domain: str
    model: str
    vector_store: str
    document_count: int
    chunk_count: int
    vector_count: int
    dimension: int
    created_at: datetime
    updated_at: datetime
    namespace: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Exceptions
class EmbeddingsError(Exception):
    """Base exception for embeddings errors"""
    pass


class ModelError(EmbeddingsError):
    """Model-related error"""
    pass


class VectorStoreError(EmbeddingsError):
    """Vector store error"""
    pass


class EmbeddingsService:
    """
    Service for generating and managing vector embeddings

    Features:
    - Text chunking with configurable overlap
    - OpenAI and local model support
    - Pinecone and Weaviate integration
    - Batch processing
    - Manifest generation
    """

    def __init__(self):
        """Initialize embeddings service"""
        self.config = EmbeddingsConfig()
        self.http_client = httpx.AsyncClient(timeout=self.config.REQUEST_TIMEOUT)

        # Initialize models
        self.local_model: Optional[SentenceTransformer] = None
        self.tokenizer = None

        # Initialize vector stores
        self.pinecone_index = None
        self.weaviate_client = None

        # Initialize tokenizer for chunking (lazy loaded)
        try:
            import tiktoken
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            logger.info("Tokenizer initialized")
        except ImportError:
            logger.warning("tiktoken not installed, using fallback token counting")
            self.tokenizer = None
        except Exception as e:
            logger.warning(f"Failed to initialize tokenizer: {e}")
            self.tokenizer = None

    def _init_local_model(self):
        """Initialize local embedding model"""
        if self.local_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.local_model = SentenceTransformer(self.config.LOCAL_MODEL_NAME)
                logger.info(f"Loaded local model: {self.config.LOCAL_MODEL_NAME}")
            except ImportError as e:
                logger.error(f"sentence-transformers not installed: {e}")
                raise ModelError("sentence-transformers library is required for local models. Please install it or use OpenAI embeddings instead.")
            except Exception as e:
                logger.error(f"Failed to load local model: {e}")
                raise ModelError(f"Failed to load local model: {str(e)}")

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
                raise VectorStoreError("pinecone library is required. Please install it or use Weaviate instead.")
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone: {e}")
                raise VectorStoreError(f"Failed to initialize Pinecone: {str(e)}")

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
                raise VectorStoreError("weaviate library is required. Please install it or use Pinecone instead.")
            except Exception as e:
                logger.error(f"Failed to initialize Weaviate: {e}")
                raise VectorStoreError(f"Failed to initialize Weaviate: {str(e)}")

    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text

        Args:
            text: Text to count

        Returns:
            Token count
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback: rough estimate
            return len(text.split()) * 1.3

    def _generate_chunk_id(self, page_url: str, chunk_index: int) -> str:
        """
        Generate unique chunk ID

        Args:
            page_url: Page URL
            chunk_index: Chunk index

        Returns:
            Unique chunk ID
        """
        content = f"{page_url}:{chunk_index}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def chunk_text(
        self,
        text: str,
        page_url: str,
        page_title: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[TextChunk]:
        """
        Chunk text into smaller pieces with overlap

        Args:
            text: Text to chunk
            page_url: Source page URL
            page_title: Page title
            metadata: Additional metadata

        Returns:
            List of text chunks
        """
        if metadata is None:
            metadata = {}

        chunks: List[TextChunk] = []

        # Split into sentences (simple approach)
        sentences = text.replace('\n', ' ').split('. ')

        current_chunk = []
        current_tokens = 0
        chunk_index = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_tokens = self._count_tokens(sentence)

            # If adding this sentence would exceed max tokens, save current chunk
            if current_tokens + sentence_tokens > self.config.MAX_CHUNK_TOKENS and current_chunk:
                chunk_text = '. '.join(current_chunk) + '.'

                if len(chunk_text) >= self.config.MIN_CHUNK_SIZE:
                    chunk_id = self._generate_chunk_id(page_url, chunk_index)
                    chunks.append(TextChunk(
                        chunk_id=chunk_id,
                        text=chunk_text,
                        page_url=page_url,
                        page_title=page_title,
                        chunk_index=chunk_index,
                        token_count=current_tokens,
                        metadata=metadata
                    ))
                    chunk_index += 1

                # Start new chunk with overlap
                overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_tokens = sum(self._count_tokens(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens

        # Add final chunk
        if current_chunk:
            chunk_text = '. '.join(current_chunk) + '.'
            if len(chunk_text) >= self.config.MIN_CHUNK_SIZE:
                chunk_id = self._generate_chunk_id(page_url, chunk_index)
                chunks.append(TextChunk(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    page_url=page_url,
                    page_title=page_title,
                    chunk_index=chunk_index,
                    token_count=current_tokens,
                    metadata=metadata
                ))

        logger.info(f"Chunked text into {len(chunks)} chunks for {page_url}")
        return chunks

    async def generate_embeddings_openai(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        Generate embeddings using OpenAI API

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            ModelError: If API call fails
        """
        headers = {
            "Authorization": f"Bearer {self.config.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "input": texts,
            "model": self.config.OPENAI_EMBEDDING_MODEL
        }

        try:
            logger.info(f"Generating OpenAI embeddings for {len(texts)} texts")
            response = await self.http_client.post(
                self.config.OPENAI_API_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()

            embeddings = [item["embedding"] for item in result["data"]]
            logger.info(f"Generated {len(embeddings)} OpenAI embeddings")
            return embeddings

        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ModelError(f"OpenAI API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {e}")
            raise ModelError(f"Failed to generate embeddings: {str(e)}")

    def generate_embeddings_local(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        Generate embeddings using local model

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            ModelError: If generation fails
        """
        self._init_local_model()

        try:
            logger.info(f"Generating local embeddings for {len(texts)} texts")
            embeddings = self.local_model.encode(texts, convert_to_numpy=True)
            embeddings_list = [emb.tolist() for emb in embeddings]
            logger.info(f"Generated {len(embeddings_list)} local embeddings")
            return embeddings_list
        except Exception as e:
            logger.error(f"Error generating local embeddings: {e}")
            raise ModelError(f"Failed to generate embeddings: {str(e)}")

    async def store_vectors_pinecone(
        self,
        vectors: List[EmbeddingVector],
        namespace: Optional[str] = None
    ):
        """
        Store vectors in Pinecone

        Args:
            vectors: Vectors to store
            namespace: Optional namespace

        Raises:
            VectorStoreError: If storage fails
        """
        self._init_pinecone()

        try:
            # Prepare vectors for upsert
            vectors_to_upsert = []
            for vec in vectors:
                metadata = {
                    "page_url": vec.chunk.page_url,
                    "page_title": vec.chunk.page_title,
                    "chunk_index": vec.chunk.chunk_index,
                    "text": vec.chunk.text,
                    "created_at": vec.created_at.isoformat()
                }
                metadata.update(vec.chunk.metadata)

                vectors_to_upsert.append((
                    vec.chunk_id,
                    vec.vector,
                    metadata
                ))

            # Batch upsert
            batch_size = self.config.MAX_BATCH_SIZE
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.pinecone_index.upsert(
                    vectors=batch,
                    namespace=namespace or ""
                )
                logger.info(f"Upserted batch {i // batch_size + 1} to Pinecone")

            logger.info(f"Stored {len(vectors)} vectors in Pinecone")

        except Exception as e:
            logger.error(f"Error storing vectors in Pinecone: {e}")
            raise VectorStoreError(f"Failed to store vectors: {str(e)}")

    async def store_vectors_weaviate(
        self,
        vectors: List[EmbeddingVector],
        namespace: Optional[str] = None
    ):
        """
        Store vectors in Weaviate

        Args:
            vectors: Vectors to store
            namespace: Optional namespace

        Raises:
            VectorStoreError: If storage fails
        """
        self._init_weaviate()

        try:
            # Batch import
            with self.weaviate_client.batch as batch:
                batch.batch_size = self.config.MAX_BATCH_SIZE

                for vec in vectors:
                    properties = {
                        "chunk_id": vec.chunk_id,
                        "page_url": vec.chunk.page_url,
                        "page_title": vec.chunk.page_title,
                        "chunk_index": vec.chunk.chunk_index,
                        "text": vec.chunk.text,
                        "created_at": vec.created_at.isoformat(),
                        "namespace": namespace or ""
                    }
                    properties.update(vec.chunk.metadata)

                    batch.add_data_object(
                        data_object=properties,
                        class_name=self.config.WEAVIATE_CLASS_NAME,
                        vector=vec.vector
                    )

            logger.info(f"Stored {len(vectors)} vectors in Weaviate")

        except Exception as e:
            logger.error(f"Error storing vectors in Weaviate: {e}")
            raise VectorStoreError(f"Failed to store vectors: {str(e)}")

    async def build_embeddings(
        self,
        request: BuildEmbeddingsRequest
    ) -> BuildEmbeddingsResponse:
        """
        Build embeddings for a domain's pages

        Args:
            request: Build request

        Returns:
            Build response

        Raises:
            EmbeddingsError: If build fails
        """
        logger.info(
            f"Building embeddings for {request.domain} "
            f"with {len(request.pages)} pages using {request.model}"
        )

        # Step 1: Chunk all pages
        all_chunks: List[TextChunk] = []
        for page in request.pages:
            chunks = self.chunk_text(
                text=page.rendered_text,
                page_url=str(page.url),
                page_title=page.title,
                metadata=page.metadata
            )
            all_chunks.extend(chunks)

        logger.info(f"Generated {len(all_chunks)} chunks from {len(request.pages)} pages")

        # Step 2: Generate embeddings
        chunk_texts = [chunk.text for chunk in all_chunks]

        if request.model == "ada-002":
            embeddings = await self.generate_embeddings_openai(chunk_texts)
            dimension = 1536  # OpenAI ada-002 dimension
        else:  # minilm
            embeddings = self.generate_embeddings_local(chunk_texts)
            dimension = self.config.LOCAL_MODEL_DIMENSION

        # Step 3: Create embedding vectors
        created_at = datetime.utcnow()
        embedding_vectors = [
            EmbeddingVector(
                chunk_id=chunk.chunk_id,
                vector=embedding,
                chunk=chunk,
                created_at=created_at
            )
            for chunk, embedding in zip(all_chunks, embeddings)
        ]

        # Step 4: Store in vector store
        if request.vector_store == "pinecone":
            await self.store_vectors_pinecone(embedding_vectors, request.namespace)
        else:  # weaviate
            await self.store_vectors_weaviate(embedding_vectors, request.namespace)

        # Step 5: Create manifest
        manifest = EmbeddingsManifest(
            domain=request.domain,
            model=request.model,
            vector_store=request.vector_store,
            document_count=len(request.pages),
            chunk_count=len(all_chunks),
            vector_count=len(embedding_vectors),
            dimension=dimension,
            created_at=created_at,
            updated_at=created_at,
            namespace=request.namespace,
            metadata={
                "pages": [str(page.url) for page in request.pages]
            }
        )

        # TODO: Store manifest (S3 or database)
        manifest_url = f"https://iaindex.com/manifests/{request.domain}/embeddings.json"

        return BuildEmbeddingsResponse(
            domain=request.domain,
            document_count=len(request.pages),
            chunk_count=len(all_chunks),
            vector_count=len(embedding_vectors),
            manifest_url=manifest_url,
            metadata=manifest.dict(),
            created_at=created_at
        )

    async def cleanup(self):
        """Cleanup resources"""
        await self.http_client.aclose()
        logger.info("Embeddings service cleaned up")


# Singleton instance
_embeddings_service: Optional[EmbeddingsService] = None


def get_embeddings_service() -> EmbeddingsService:
    """Get or create embeddings service instance"""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service
