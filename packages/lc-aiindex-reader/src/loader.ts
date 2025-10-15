/**
 * AIIndexLoader - LangChain document loader for AIIndex
 */

import { Document } from '@langchain/core/documents';
import { BaseDocumentLoader } from '@langchain/core/document_loaders/base';
import { AIIndexReader } from './reader';
import { AIIndexReceiptSigner } from './signer';
import type { AIIndexDocument, AIIndexLoaderOptions, Page } from './types';

export class AIIndexLoader extends BaseDocumentLoader {
  private reader: AIIndexReader;
  private signer?: AIIndexReceiptSigner;
  private url: string;
  private options: AIIndexLoaderOptions;

  constructor(url: string, options: AIIndexLoaderOptions = {}) {
    super();
    this.url = url;
    this.options = options;

    this.reader = new AIIndexReader({
      timeout: options.timeout,
      validateSchema: options.validateSchema,
      clientId: options.clientId,
      clientName: options.clientName,
      clientVersion: options.clientVersion,
    });

    // Initialize signer if keys are provided
    if (options.privateKeyPem && options.keyId) {
      this.signer = new AIIndexReceiptSigner({
        clientId: options.clientId || 'langchain-client',
        clientName: options.clientName,
        clientVersion: options.clientVersion,
        privateKeyPem: options.privateKeyPem,
        keyId: options.keyId,
        algorithm: options.algorithm,
      });
    }
  }

  /**
   * Load documents from ai-index.json
   */
  async load(): Promise<Document[]> {
    try {
      // Fetch the ai-index.json document
      const aiIndexDoc = await this.reader.fetch(this.url);

      // Create receipt if signer is available
      if (this.signer && this.options.autoSendReceipt) {
        await this.createAndSendReceipt(aiIndexDoc);
      }

      // Convert to LangChain documents
      const documents = this.convertToDocuments(aiIndexDoc);

      return documents;
    } catch (error) {
      console.error('Failed to load ai-index.json:', error);
      throw error;
    }
  }

  /**
   * Convert AIIndex document to LangChain Document format
   */
  private convertToDocuments(aiIndexDoc: AIIndexDocument): Document[] {
    const documents: Document[] = [];
    const includeMetadata = this.options.includeMetadata !== false;
    const filterContentType = this.options.filterContentType;
    const maxPages = this.options.maxPages;

    // Add publisher information as a document
    if (aiIndexDoc.publisher) {
      const publisherContent = this.formatPublisher(aiIndexDoc);
      documents.push(
        new Document({
          pageContent: publisherContent,
          metadata: includeMetadata
            ? {
                source: this.url,
                type: 'publisher',
                publisher_id: aiIndexDoc.publisher_id,
                domain: aiIndexDoc.domain,
                last_updated: aiIndexDoc.last_updated,
              }
            : {},
        })
      );
    }

    // Add entities as documents
    if (aiIndexDoc.entities && aiIndexDoc.entities.length > 0) {
      for (const entity of aiIndexDoc.entities) {
        const entityContent = this.formatEntity(entity);
        documents.push(
          new Document({
            pageContent: entityContent,
            metadata: includeMetadata
              ? {
                  source: this.url,
                  type: 'entity',
                  entity_type: entity.type,
                  entity_name: entity.name,
                  entity_url: entity.url,
                }
              : {},
          })
        );
      }
    }

    // Add pages as documents
    if (aiIndexDoc.pages && aiIndexDoc.pages.length > 0) {
      let pages = aiIndexDoc.pages;

      // Filter by content type if specified
      if (filterContentType && filterContentType.length > 0) {
        pages = pages.filter((page) =>
          page.content_type && filterContentType.includes(page.content_type)
        );
      }

      // Limit number of pages if specified
      if (maxPages && maxPages > 0) {
        pages = pages.slice(0, maxPages);
      }

      for (const page of pages) {
        const pageContent = this.formatPage(page);
        documents.push(
          new Document({
            pageContent: pageContent,
            metadata: includeMetadata
              ? {
                  source: page.url,
                  type: 'page',
                  title: page.title,
                  content_type: page.content_type,
                  author: page.author,
                  published: page.published,
                  modified: page.modified,
                  tags: page.tags,
                  ai_index_source: this.url,
                }
              : {},
          })
        );
      }
    }

    // Add FAQs as documents
    if (aiIndexDoc.faq && aiIndexDoc.faq.length > 0) {
      for (const faqItem of aiIndexDoc.faq) {
        const faqContent = this.formatFAQ(faqItem);
        documents.push(
          new Document({
            pageContent: faqContent,
            metadata: includeMetadata
              ? {
                  source: this.url,
                  type: 'faq',
                  category: faqItem.category,
                }
              : {},
          })
        );
      }
    }

    return documents;
  }

  /**
   * Format publisher information
   */
  private formatPublisher(aiIndexDoc: AIIndexDocument): string {
    const pub = aiIndexDoc.publisher;
    if (!pub) return '';

    let content = `# ${pub.name || aiIndexDoc.domain}\n\n`;

    if (pub.description) {
      content += `${pub.description}\n\n`;
    }

    if (pub.url) {
      content += `Website: ${pub.url}\n`;
    }

    if (pub.contact?.email) {
      content += `Contact: ${pub.contact.email}\n`;
    }

    return content.trim();
  }

  /**
   * Format entity information
   */
  private formatEntity(entity: any): string {
    let content = `# ${entity.name}\n\n`;
    content += `Type: ${entity.type}\n\n`;

    if (entity.description) {
      content += `${entity.description}\n\n`;
    }

    if (entity.url) {
      content += `URL: ${entity.url}\n`;
    }

    if (entity.properties) {
      content += `\nAdditional Information:\n`;
      for (const [key, value] of Object.entries(entity.properties)) {
        content += `- ${key}: ${value}\n`;
      }
    }

    return content.trim();
  }

  /**
   * Format page information
   */
  private formatPage(page: Page): string {
    let content = `# ${page.title}\n\n`;

    if (page.description) {
      content += `${page.description}\n\n`;
    }

    if (page.summary) {
      content += `${page.summary}\n\n`;
    }

    content += `URL: ${page.url}\n`;

    if (page.author) {
      content += `Author: ${page.author}\n`;
    }

    if (page.published) {
      content += `Published: ${page.published}\n`;
    }

    if (page.tags && page.tags.length > 0) {
      content += `Tags: ${page.tags.join(', ')}\n`;
    }

    return content.trim();
  }

  /**
   * Format FAQ item
   */
  private formatFAQ(faq: any): string {
    let content = `Q: ${faq.question}\n\n`;
    content += `A: ${faq.answer}`;

    if (faq.category) {
      content += `\n\nCategory: ${faq.category}`;
    }

    return content.trim();
  }

  /**
   * Create and send receipt
   */
  private async createAndSendReceipt(aiIndexDoc: AIIndexDocument): Promise<void> {
    if (!this.signer) return;

    try {
      await this.signer.createAndPostReceipt(aiIndexDoc, {
        url: this.url,
        statusCode: 200,
        purpose: {
          type: 'inference',
          description: 'Document loading for LangChain application',
          commercial: false,
        },
        attribution: {
          method: 'citation',
          citation_text: `Data from ${aiIndexDoc.domain}`,
        },
      });
    } catch (error) {
      console.error('Failed to send receipt:', error);
      // Don't fail the entire load operation if receipt fails
    }
  }

  /**
   * Load and split documents by type
   */
  async loadByType(): Promise<{
    publisher?: Document;
    entities: Document[];
    pages: Document[];
    faqs: Document[];
  }> {
    const allDocs = await this.load();

    return {
      publisher: allDocs.find((doc) => doc.metadata.type === 'publisher'),
      entities: allDocs.filter((doc) => doc.metadata.type === 'entity'),
      pages: allDocs.filter((doc) => doc.metadata.type === 'page'),
      faqs: allDocs.filter((doc) => doc.metadata.type === 'faq'),
    };
  }

  /**
   * Load multiple ai-index.json files in batch
   */
  static async loadBatch(
    urls: string[],
    options: AIIndexLoaderOptions = {}
  ): Promise<Document[]> {
    const loaders = urls.map((url) => new AIIndexLoader(url, options));
    const results = await Promise.allSettled(loaders.map((loader) => loader.load()));

    const documents: Document[] = [];
    results.forEach((result, index) => {
      if (result.status === 'fulfilled') {
        documents.push(...result.value);
      } else {
        console.error(`Failed to load ${urls[index]}:`, result.reason);
      }
    });

    return documents;
  }
}
