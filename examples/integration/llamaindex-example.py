#!/usr/bin/env python3
"""
LlamaIndex Integration Example for AIIndex

This example demonstrates how to:
1. Fetch and parse ai-index.json files
2. Create custom readers for LlamaIndex
3. Send access receipts
4. Build a RAG system with attribution

Requirements:
    pip install llama-index openai requests
"""

import json
import uuid
import requests
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from llama_index.core import (
    VectorStoreIndex,
    Document,
    ServiceContext,
    StorageContext,
)
from llama_index.core.schema import NodeWithScore
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding


@dataclass
class AIIndexPage:
    """Represents a page from ai-index.json"""
    url: str
    title: str
    description: Optional[str] = None
    content_type: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None


@dataclass
class AIIndexConfig:
    """Represents parsed ai-index.json"""
    version: str
    publisher_id: str
    domain: str
    publisher_name: str
    publisher_url: str
    pages: List[AIIndexPage]
    access_policy: Optional[Dict[str, Any]] = None


class AIIndexReader:
    """
    LlamaIndex reader for AIIndex-enabled websites
    """

    def __init__(
        self,
        domain: str,
        client_id: str = "llamaindex-app",
        client_name: str = "LlamaIndex Application",
    ):
        self.domain = domain
        self.client_id = client_id
        self.client_name = client_name
        self.ai_index_url = f"https://{domain}/.well-known/ai-index.json"

    def fetch_ai_index(self) -> AIIndexConfig:
        """Fetch and parse ai-index.json"""
        try:
            response = requests.get(self.ai_index_url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Parse pages
            pages = [
                AIIndexPage(
                    url=page["url"],
                    title=page["title"],
                    description=page.get("description"),
                    content_type=page.get("content_type"),
                    summary=page.get("summary"),
                    tags=page.get("tags", []),
                )
                for page in data.get("pages", [])
            ]

            return AIIndexConfig(
                version=data["version"],
                publisher_id=data["publisher_id"],
                domain=data["domain"],
                publisher_name=data["publisher"]["name"],
                publisher_url=data["publisher"]["url"],
                pages=pages,
                access_policy=data.get("access_policy"),
            )
        except Exception as e:
            raise Exception(f"Failed to fetch ai-index.json: {e}")

    def load_data(self) -> List[Document]:
        """Load documents from AIIndex"""
        ai_index = self.fetch_ai_index()

        # Check if access is allowed
        if ai_index.access_policy and not ai_index.access_policy.get("allowed", True):
            raise Exception(f"AI access not allowed for {self.domain}")

        # Convert pages to LlamaIndex documents
        documents = []
        for page in ai_index.pages:
            # Use summary if available, otherwise description
            content = page.summary or page.description or ""

            if not content:
                continue

            # Create document with metadata
            doc = Document(
                text=content,
                metadata={
                    "source": page.url,
                    "title": page.title,
                    "content_type": page.content_type or "page",
                    "tags": page.tags or [],
                    "publisher": ai_index.publisher_name,
                    "publisher_domain": self.domain,
                    "publisher_url": ai_index.publisher_url,
                    "attribution_required": ai_index.access_policy.get(
                        "attribution_required", False
                    )
                    if ai_index.access_policy
                    else False,
                },
            )
            documents.append(doc)

        # Send access receipt if required
        if ai_index.access_policy and ai_index.access_policy.get("receipt_required"):
            self._send_receipt(ai_index, [doc.metadata["source"] for doc in documents])

        print(f"✓ Loaded {len(documents)} documents from {self.domain}")
        return documents

    def _send_receipt(self, ai_index: AIIndexConfig, pages_accessed: List[str]):
        """Send access receipt to publisher webhook"""
        webhook_url = (
            ai_index.access_policy.get("webhook_url") if ai_index.access_policy else None
        )

        if not webhook_url:
            print("⚠ Receipt required but no webhook URL provided")
            return

        receipt = {
            "version": "1.0",
            "receipt_id": str(uuid.uuid4()),
            "publisher_id": ai_index.publisher_id,
            "publisher_domain": self.domain,
            "client_id": self.client_id,
            "client_name": self.client_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "access": {
                "url": self.ai_index_url,
                "method": "GET",
                "status_code": 200,
                "pages_accessed": pages_accessed,
            },
            "purpose": {
                "type": "inference",
                "description": "RAG system for answering user queries",
                "commercial": True,  # Adjust based on your use case
            },
            "attribution": {
                "method": "citation",
                "citation_text": f"Information from {ai_index.publisher_name}",
            },
        }

        try:
            response = requests.post(
                webhook_url,
                json=receipt,
                headers={"Content-Type": "application/json"},
                timeout=5,
            )
            response.raise_for_status()
            print(f"✓ Receipt sent to {self.domain}")
        except Exception as e:
            print(f"✗ Failed to send receipt: {e}")


class AIIndexRAG:
    """
    RAG system with AIIndex integration and attribution
    """

    def __init__(self, openai_api_key: str):
        # Initialize LLM and embeddings
        self.llm = OpenAI(model="gpt-4", api_key=openai_api_key, temperature=0.7)
        self.embed_model = OpenAIEmbedding(api_key=openai_api_key)

        # Initialize service context
        self.service_context = ServiceContext.from_defaults(
            llm=self.llm, embed_model=self.embed_model
        )

        self.index = None
        self.query_engine = None

    def add_domains(self, domains: List[str]):
        """Add documents from AIIndex-enabled domains"""
        all_documents = []

        for domain in domains:
            print(f"Loading documents from {domain}...")
            reader = AIIndexReader(domain, "my-llamaindex-app", "My LlamaIndex App")

            try:
                documents = reader.load_data()
                all_documents.extend(documents)
            except Exception as e:
                print(f"✗ Failed to load {domain}: {e}")

        # Create index
        self.index = VectorStoreIndex.from_documents(
            all_documents, service_context=self.service_context
        )

        # Create query engine with attribution prompt
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=3,
        )

        response_synthesizer = get_response_synthesizer(
            service_context=self.service_context,
            response_mode="compact",
        )

        self.query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
        )

        print(f"✓ RAG system ready with {len(all_documents)} documents")

    def query(self, question: str) -> Dict[str, Any]:
        """Query the RAG system with attribution"""
        if not self.query_engine:
            raise Exception("RAG system not initialized. Call add_domains() first.")

        # Add attribution instruction to question
        attributed_question = f"""
{question}

IMPORTANT: Always cite your sources when using information from the context.
Format citations as: "According to [Publisher Name]..." or "Source: [Publisher Name]"
        """

        response = self.query_engine.query(attributed_question)

        # Extract sources for attribution
        sources = []
        if hasattr(response, "source_nodes"):
            for node in response.source_nodes:
                sources.append(
                    {
                        "source": node.metadata.get("source"),
                        "publisher": node.metadata.get("publisher"),
                        "title": node.metadata.get("title"),
                        "score": node.score if hasattr(node, "score") else None,
                    }
                )

        return {
            "answer": str(response),
            "sources": sources,
        }


class AIIndexRetriever:
    """
    Custom retriever with AIIndex metadata filtering
    """

    def __init__(self, index: VectorStoreIndex):
        self.index = index

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        filter_publisher: Optional[str] = None,
        filter_content_type: Optional[str] = None,
    ) -> List[NodeWithScore]:
        """Retrieve documents with metadata filtering"""
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=top_k * 3,  # Get more then filter
        )

        # Retrieve documents
        nodes = retriever.retrieve(query)

        # Apply filters
        filtered_nodes = nodes

        if filter_publisher:
            filtered_nodes = [
                node
                for node in filtered_nodes
                if node.metadata.get("publisher_domain") == filter_publisher
            ]

        if filter_content_type:
            filtered_nodes = [
                node
                for node in filtered_nodes
                if node.metadata.get("content_type") == filter_content_type
            ]

        # Return top k
        return filtered_nodes[:top_k]

    def get_attribution_text(self, nodes: List[NodeWithScore]) -> str:
        """Generate attribution text from retrieved nodes"""
        publishers = set(node.metadata.get("publisher") for node in nodes)
        publishers.discard(None)

        if not publishers:
            return ""
        if len(publishers) == 1:
            return f"Source: {list(publishers)[0]}"

        return f"Sources: {', '.join(publishers)}"


def main():
    """Example usage"""
    import os

    # Initialize RAG system
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")

    rag = AIIndexRAG(api_key)

    # Add multiple AIIndex-enabled domains
    rag.add_domains(
        [
            "example-blog.com",
            "cloudforge-docs.dev",
            "techgear-shop.com",
        ]
    )

    # Query the system
    questions = [
        "What are AI agents and how do they work?",
        "How do I deploy an application with CloudForge?",
        "What mechanical keyboards do you recommend for developers?",
    ]

    for question in questions:
        print(f"\n❓ {question}")

        result = rag.query(question)

        print(f"\n💬 {result['answer']}")
        print("\n📚 Sources:")
        for source in result["sources"]:
            print(f"  - {source['publisher']}: {source['source']}")
            if source["score"]:
                print(f"    Relevance: {source['score']:.3f}")


def example_custom_retriever():
    """Example using custom retriever with filtering"""
    import os

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")

    # Load documents
    all_documents = []
    for domain in ["example-blog.com", "techgear-shop.com"]:
        reader = AIIndexReader(domain)
        documents = reader.load_data()
        all_documents.extend(documents)

    # Create index
    llm = OpenAI(model="gpt-4", api_key=api_key)
    embed_model = OpenAIEmbedding(api_key=api_key)
    service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)

    index = VectorStoreIndex.from_documents(
        all_documents, service_context=service_context
    )

    # Create custom retriever
    retriever = AIIndexRetriever(index)

    # Retrieve with filtering
    query = "mechanical keyboards"
    nodes = retriever.retrieve(
        query, top_k=3, filter_publisher="techgear-shop.com", filter_content_type="product"
    )

    print(f"\nRetrieved {len(nodes)} nodes for '{query}':")
    for node in nodes:
        print(f"\n- {node.metadata.get('title')}")
        print(f"  Publisher: {node.metadata.get('publisher')}")
        print(f"  URL: {node.metadata.get('source')}")
        print(f"  Score: {node.score:.3f}")

    # Get attribution
    attribution = retriever.get_attribution_text(nodes)
    print(f"\n{attribution}")


if __name__ == "__main__":
    # Run main example
    main()

    # Uncomment to run custom retriever example
    # example_custom_retriever()
