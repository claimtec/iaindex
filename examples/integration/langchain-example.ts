/**
 * LangChain Integration Example for AIIndex
 *
 * This example demonstrates how to:
 * 1. Fetch and parse ai-index.json files
 * 2. Create a custom document loader
 * 3. Send access receipts
 * 4. Use AIIndex data with LangChain RAG
 *
 * Requirements:
 * - npm install langchain @langchain/openai @langchain/community
 * - npm install @aiindex/sdk-node
 */

import { OpenAI } from "@langchain/openai";
import { OpenAIEmbeddings } from "@langchain/openai";
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { Document } from "@langchain/core/documents";
import { RetrievalQAChain } from "langchain/chains";
import { PromptTemplate } from "@langchain/core/prompts";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";

// AIIndex interfaces
interface AIIndexPage {
  url: string;
  title: string;
  description?: string;
  content_type?: string;
  summary?: string;
  tags?: string[];
}

interface AIIndexConfig {
  version: string;
  publisher_id: string;
  domain: string;
  publisher: {
    name: string;
    description?: string;
    url: string;
  };
  pages: AIIndexPage[];
  access_policy?: {
    allowed: boolean;
    attribution_required: boolean;
    receipt_required: boolean;
    webhook_url?: string;
  };
}

interface AccessReceipt {
  version: string;
  receipt_id: string;
  publisher_id: string;
  publisher_domain: string;
  client_id: string;
  client_name: string;
  timestamp: string;
  access: {
    url: string;
    method: string;
    status_code: number;
    pages_accessed: string[];
  };
  purpose: {
    type: string;
    description: string;
    commercial: boolean;
  };
  attribution: {
    method: string;
    citation_text: string;
  };
}

/**
 * AIIndex Document Loader for LangChain
 */
class AIIndexLoader {
  private domain: string;
  private clientId: string;
  private clientName: string;
  private aiIndexUrl: string;

  constructor(
    domain: string,
    clientId: string = "langchain-app",
    clientName: string = "LangChain Application"
  ) {
    this.domain = domain;
    this.clientId = clientId;
    this.clientName = clientName;
    this.aiIndexUrl = `https://${domain}/.well-known/ai-index.json`;
  }

  /**
   * Fetch and parse ai-index.json
   */
  async fetchAIIndex(): Promise<AIIndexConfig> {
    try {
      const response = await axios.get(this.aiIndexUrl);
      return response.data as AIIndexConfig;
    } catch (error) {
      throw new Error(`Failed to fetch ai-index.json: ${error}`);
    }
  }

  /**
   * Convert AIIndex pages to LangChain documents
   */
  async load(): Promise<Document[]> {
    const aiIndex = await this.fetchAIIndex();

    // Check if access is allowed
    if (aiIndex.access_policy && !aiIndex.access_policy.allowed) {
      throw new Error(`AI access not allowed for ${this.domain}`);
    }

    // Convert pages to documents
    const documents = aiIndex.pages.map((page) => {
      const content = page.summary || page.description || "";
      const metadata = {
        source: page.url,
        title: page.title,
        content_type: page.content_type || "page",
        tags: page.tags || [],
        publisher: aiIndex.publisher.name,
        publisher_domain: this.domain,
        attribution_required: aiIndex.access_policy?.attribution_required || false,
      };

      return new Document({
        pageContent: content,
        metadata,
      });
    });

    // Send access receipt if required
    if (aiIndex.access_policy?.receipt_required) {
      await this.sendReceipt(aiIndex, documents.map((d) => d.metadata.source));
    }

    return documents;
  }

  /**
   * Send access receipt to publisher webhook
   */
  private async sendReceipt(
    aiIndex: AIIndexConfig,
    pagesAccessed: string[]
  ): Promise<void> {
    if (!aiIndex.access_policy?.webhook_url) {
      console.warn("Receipt required but no webhook URL provided");
      return;
    }

    const receipt: AccessReceipt = {
      version: "1.0",
      receipt_id: uuidv4(),
      publisher_id: aiIndex.publisher_id,
      publisher_domain: this.domain,
      client_id: this.clientId,
      client_name: this.clientName,
      timestamp: new Date().toISOString(),
      access: {
        url: this.aiIndexUrl,
        method: "GET",
        status_code: 200,
        pages_accessed: pagesAccessed,
      },
      purpose: {
        type: "inference",
        description: "RAG system for answering user queries",
        commercial: true, // Adjust based on your use case
      },
      attribution: {
        method: "citation",
        citation_text: `Information from ${aiIndex.publisher.name}`,
      },
    };

    try {
      await axios.post(aiIndex.access_policy.webhook_url, receipt, {
        headers: { "Content-Type": "application/json" },
      });
      console.log(`✓ Receipt sent to ${this.domain}`);
    } catch (error) {
      console.error(`Failed to send receipt: ${error}`);
    }
  }
}

/**
 * AIIndex-aware RAG System
 */
class AIIndexRAG {
  private model: OpenAI;
  private embeddings: OpenAIEmbeddings;
  private vectorStore?: MemoryVectorStore;
  private chain?: RetrievalQAChain;

  constructor(openaiApiKey: string) {
    this.model = new OpenAI({
      openAIApiKey: openaiApiKey,
      modelName: "gpt-4",
      temperature: 0.7,
    });

    this.embeddings = new OpenAIEmbeddings({
      openAIApiKey: openaiApiKey,
    });
  }

  /**
   * Add documents from AIIndex domains
   */
  async addDomains(domains: string[]): Promise<void> {
    const allDocuments: Document[] = [];

    for (const domain of domains) {
      console.log(`Loading documents from ${domain}...`);
      const loader = new AIIndexLoader(domain, "my-langchain-app", "My LangChain App");

      try {
        const documents = await loader.load();
        allDocuments.push(...documents);
        console.log(`✓ Loaded ${documents.length} documents from ${domain}`);
      } catch (error) {
        console.error(`Failed to load ${domain}: ${error}`);
      }
    }

    // Create vector store
    this.vectorStore = await MemoryVectorStore.fromDocuments(
      allDocuments,
      this.embeddings
    );

    // Create retrieval chain with attribution
    const prompt = PromptTemplate.fromTemplate(`
You are a helpful assistant that answers questions based on provided context.

IMPORTANT: Always cite your sources when using information from the context.
Format citations as: "According to [Source Name]..." or "Source: [Source Name]"

Context:
{context}

Question: {question}

Answer with citations:
    `);

    this.chain = RetrievalQAChain.fromLLM(
      this.model,
      this.vectorStore.asRetriever({ k: 3 }),
      {
        prompt,
        returnSourceDocuments: true,
      }
    );

    console.log(`✓ RAG system ready with ${allDocuments.length} documents`);
  }

  /**
   * Query the RAG system
   */
  async query(question: string): Promise<{
    answer: string;
    sources: Array<{ source: string; publisher: string }>;
  }> {
    if (!this.chain) {
      throw new Error("RAG system not initialized. Call addDomains() first.");
    }

    const response = await this.chain.call({
      query: question,
    });

    // Extract sources for attribution
    const sources = response.sourceDocuments.map((doc: Document) => ({
      source: doc.metadata.source,
      publisher: doc.metadata.publisher,
      title: doc.metadata.title,
    }));

    return {
      answer: response.text,
      sources,
    };
  }
}

/**
 * Example usage
 */
async function main() {
  // Initialize RAG system
  const rag = new AIIndexRAG(process.env.OPENAI_API_KEY!);

  // Add multiple AIIndex-enabled domains
  await rag.addDomains([
    "example-blog.com",
    "cloudforge-docs.dev",
    "techgear-shop.com",
  ]);

  // Query the system
  const questions = [
    "What are AI agents and how do they work?",
    "How do I deploy an application with CloudForge?",
    "What mechanical keyboards do you recommend for developers?",
  ];

  for (const question of questions) {
    console.log(`\n❓ ${question}`);

    const result = await rag.query(question);

    console.log(`\n💬 ${result.answer}`);
    console.log("\n📚 Sources:");
    result.sources.forEach((source) => {
      console.log(`  - ${source.publisher}: ${source.source}`);
    });
  }
}

/**
 * Advanced: Custom retriever with AIIndex metadata
 */
class AIIndexRetriever {
  private vectorStore: MemoryVectorStore;

  constructor(vectorStore: MemoryVectorStore) {
    this.vectorStore = vectorStore;
  }

  /**
   * Retrieve documents with attribution metadata
   */
  async retrieve(
    query: string,
    options: {
      k?: number;
      filterByPublisher?: string;
      filterByContentType?: string;
    } = {}
  ): Promise<Document[]> {
    const { k = 3, filterByPublisher, filterByContentType } = options;

    // Get all similar documents
    const allDocs = await this.vectorStore.similaritySearch(query, k * 3);

    // Filter by metadata
    let filtered = allDocs;

    if (filterByPublisher) {
      filtered = filtered.filter(
        (doc) => doc.metadata.publisher_domain === filterByPublisher
      );
    }

    if (filterByContentType) {
      filtered = filtered.filter(
        (doc) => doc.metadata.content_type === filterByContentType
      );
    }

    // Return top k
    return filtered.slice(0, k);
  }

  /**
   * Get attribution text for documents
   */
  getAttributionText(documents: Document[]): string {
    const publishers = new Set(
      documents.map((doc) => doc.metadata.publisher)
    );

    if (publishers.size === 0) return "";
    if (publishers.size === 1) {
      return `Source: ${Array.from(publishers)[0]}`;
    }

    return `Sources: ${Array.from(publishers).join(", ")}`;
  }
}

// Export for use in other modules
export {
  AIIndexLoader,
  AIIndexRAG,
  AIIndexRetriever,
  AIIndexConfig,
  AccessReceipt,
};

// Run example if executed directly
if (require.main === module) {
  main().catch(console.error);
}
