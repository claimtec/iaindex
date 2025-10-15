/**
 * AIIndexReader - Fetch and parse ai-index.json files with schema validation
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import Ajv, { JSONSchemaType } from 'ajv';
import addFormats from 'ajv-formats';
import type { AIIndexDocument, AIIndexReaderOptions, ValidationResult, AIIndexPolicy } from './types';
import { PolicyEnforcer, parseDomain } from './policy';
import { RenderFallbackAdapter } from './renderer';

export class AIIndexReader {
  private client: AxiosInstance;
  private options: Required<AIIndexReaderOptions>;
  private ajv: Ajv;
  private policyEnforcer: PolicyEnforcer;
  private renderAdapter: RenderFallbackAdapter;

  constructor(options: AIIndexReaderOptions = {}) {
    this.options = {
      timeout: options.timeout || 10000,
      validateSchema: options.validateSchema !== false,
      autoSendReceipt: options.autoSendReceipt || false,
      clientId: options.clientId || 'langchain-client',
      clientName: options.clientName || 'LangChain AIIndex Reader',
      clientVersion: options.clientVersion || '1.0.0',
      privateKeyPem: options.privateKeyPem || '',
      keyId: options.keyId || '',
      algorithm: options.algorithm || 'ES256',
      intent: options.intent || 'retrieval',
      respectPolicyBlocks: options.respectPolicyBlocks !== false,
      enableRenderFallback: options.enableRenderFallback !== false,
    };

    this.client = axios.create({
      timeout: this.options.timeout,
      headers: {
        'User-Agent': `${this.options.clientName}/${this.options.clientVersion}`,
        'Accept': 'application/json',
        'X-AIIndex-Version': 'v1.1',
        'X-AIIndex-Client-ID': this.options.clientId,
        'X-AIIndex-Intent': this.options.intent,
      },
    });

    this.ajv = new Ajv({ allErrors: true });
    addFormats(this.ajv);

    this.policyEnforcer = new PolicyEnforcer(this.options.timeout);
    this.renderAdapter = new RenderFallbackAdapter(this.options.timeout);
  }

  /**
   * Fetch and parse ai-index.json from a URL or domain with policy enforcement
   */
  async fetch(urlOrDomain: string, intent?: 'training' | 'retrieval'): Promise<AIIndexDocument> {
    const resolvedIntent = intent || this.options.intent;
    const domain = parseDomain(urlOrDomain);

    try {
      const url = this.normalizeUrl(urlOrDomain);

      // First, try to fetch the document
      let document: AIIndexDocument;
      let policy: AIIndexPolicy | null = null;

      try {
        const response = await this.client.get<AIIndexDocument>(url);

        if (response.status !== 200) {
          throw new Error(`Failed to fetch ai-index.json: HTTP ${response.status}`);
        }

        document = response.data;

        // Fetch and evaluate policy
        if (this.options.respectPolicyBlocks) {
          policy = await this.policyEnforcer.fetchPolicy(domain, document);
          const evaluation = await this.policyEnforcer.evaluatePolicy(domain, resolvedIntent, document);

          // Apply rate limiting if policy exists
          if (policy) {
            await this.policyEnforcer.applyRateLimit(domain, policy);
          }
        }

        // Validate schema if enabled
        if (this.options.validateSchema) {
          const validation = this.validate(document);
          if (!validation.valid) {
            console.warn('Schema validation warnings:', validation.errors);
          }
        }

        return document;
      } catch (fetchError) {
        if (axios.isAxiosError(fetchError)) {
          const axiosError = fetchError as AxiosError;

          // Handle 403 Forbidden - check for denial receipt
          if (axiosError.response?.status === 403) {
            const denialReceipt = this.policyEnforcer.parseDenialReceipt(axiosError);
            if (denialReceipt) {
              throw new Error(
                `Access denied (403): ${denialReceipt.reason}${
                  denialReceipt.retry_after ? ` - Retry after ${denialReceipt.retry_after}s` : ''
                }`
              );
            }
          }

          // Handle 404 Not Found - try render fallback if enabled
          if (axiosError.response?.status === 404 && this.options.enableRenderFallback) {
            console.log('ai-index.json not found, trying render fallback...');
            const renderResponse = await this.renderAdapter.fetchRenderedContent(
              domain,
              undefined,
              this.options.clientId,
              resolvedIntent
            );

            if (renderResponse?.rendered_text) {
              // Create a synthetic AIIndexDocument from rendered content
              const syntheticDoc: AIIndexDocument = {
                version: '1.1',
                publisher_id: domain,
                domain: domain,
                last_updated: new Date().toISOString(),
                publisher: {
                  name: domain,
                  description: 'Content from render fallback',
                },
                pages: [
                  {
                    url: renderResponse.url,
                    title: domain,
                    summary: renderResponse.rendered_text.substring(0, 500),
                  },
                ],
                metadata: {
                  source: 'render-fallback',
                  ...renderResponse.metadata,
                },
              };

              return syntheticDoc;
            }
          }
        }

        throw fetchError;
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError;
        if (axiosError.response) {
          throw new Error(
            `Failed to fetch ai-index.json: HTTP ${axiosError.response.status} - ${axiosError.message}`
          );
        } else if (axiosError.request) {
          throw new Error(`Network error: ${axiosError.message}`);
        }
      }
      throw error;
    }
  }

  /**
   * Fetch multiple ai-index.json files in batch
   */
  async fetchBatch(urls: string[]): Promise<Array<{ url: string; document?: AIIndexDocument; error?: string }>> {
    const results = await Promise.allSettled(
      urls.map(async (url) => ({
        url,
        document: await this.fetch(url),
      }))
    );

    return results.map((result, index) => {
      if (result.status === 'fulfilled') {
        return result.value;
      } else {
        return {
          url: urls[index],
          error: result.reason?.message || 'Unknown error',
        };
      }
    });
  }

  /**
   * Validate ai-index.json against schema
   */
  validate(document: any): ValidationResult {
    const schema = this.getSchema();
    const validate = this.ajv.compile(schema);
    const valid = validate(document);

    if (!valid && validate.errors) {
      return {
        valid: false,
        errors: validate.errors.map((err) => ({
          field: err.instancePath || err.schemaPath,
          message: err.message || 'Validation error',
        })),
      };
    }

    return { valid: true };
  }

  /**
   * Check if a domain has an ai-index.json file
   */
  async probe(domain: string): Promise<boolean> {
    try {
      const url = this.normalizeUrl(domain);
      const response = await this.client.head(url);
      return response.status === 200;
    } catch {
      return false;
    }
  }

  /**
   * Get content hash (SHA-256) of the document
   */
  async getContentHash(document: AIIndexDocument): Promise<string> {
    const content = JSON.stringify(document, null, 0);
    const crypto = await import('crypto');
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  /**
   * Normalize URL to ai-index.json endpoint
   */
  private normalizeUrl(urlOrDomain: string): string {
    // If it's already a full URL to ai-index.json, return as-is
    if (urlOrDomain.includes('ai-index.json')) {
      return urlOrDomain;
    }

    // Remove protocol if present
    let domain = urlOrDomain.replace(/^https?:\/\//, '');

    // Remove trailing slash
    domain = domain.replace(/\/$/, '');

    // Remove path if present
    domain = domain.split('/')[0];

    // Construct full URL
    return `https://${domain}/ai-index.json`;
  }

  /**
   * Get AIIndex JSON Schema
   */
  private getSchema(): JSONSchemaType<any> {
    return {
      type: 'object',
      properties: {
        version: { type: 'string' },
        publisher_id: { type: 'string' },
        domain: { type: 'string' },
        last_updated: { type: 'string' },
        publisher: {
          type: 'object',
          properties: {
            name: { type: 'string', nullable: true },
            description: { type: 'string', nullable: true },
            url: { type: 'string', nullable: true },
            contact: {
              type: 'object',
              properties: {
                email: { type: 'string', nullable: true },
                url: { type: 'string', nullable: true },
              },
              nullable: true,
            },
            logo: { type: 'string', nullable: true },
          },
          nullable: true,
        },
        entities: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              type: { type: 'string' },
              name: { type: 'string' },
              description: { type: 'string', nullable: true },
              url: { type: 'string', nullable: true },
              image: { type: 'string', nullable: true },
              properties: { type: 'object', nullable: true },
            },
            required: ['type', 'name'],
          },
          nullable: true,
        },
        pages: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              url: { type: 'string' },
              title: { type: 'string' },
              description: { type: 'string', nullable: true },
              content_type: { type: 'string', nullable: true },
              published: { type: 'string', nullable: true },
              modified: { type: 'string', nullable: true },
              author: { type: 'string', nullable: true },
              tags: { type: 'array', items: { type: 'string' }, nullable: true },
              summary: { type: 'string', nullable: true },
            },
            required: ['url', 'title'],
          },
          nullable: true,
        },
        faq: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              question: { type: 'string' },
              answer: { type: 'string' },
              category: { type: 'string', nullable: true },
            },
            required: ['question', 'answer'],
          },
          nullable: true,
        },
        access_policy: {
          type: 'object',
          properties: {
            allowed: { type: 'boolean' },
            attribution_required: { type: 'boolean' },
            commercial_use: { type: 'boolean' },
            receipt_required: { type: 'boolean' },
            webhook_url: { type: 'string', nullable: true },
          },
          nullable: true,
        },
        signature: {
          type: 'object',
          properties: {
            algorithm: { type: 'string' },
            kid: { type: 'string' },
            signature: { type: 'string' },
            document_hash: { type: 'string' },
            signed_at: { type: 'string', nullable: true },
          },
          nullable: true,
        },
        verification: {
          type: 'object',
          properties: {
            verified: { type: 'boolean', nullable: true },
            verified_at: { type: 'string', nullable: true },
            verification_url: { type: 'string', nullable: true },
          },
          nullable: true,
        },
        metadata: { type: 'object', nullable: true },
      },
      required: ['version', 'publisher_id', 'domain', 'last_updated'],
    };
  }

  /**
   * Extract all page URLs from the document
   */
  extractPageUrls(document: AIIndexDocument): string[] {
    return document.pages?.map((page) => page.url) || [];
  }

  /**
   * Extract entities by type
   */
  extractEntitiesByType(document: AIIndexDocument, type: string): any[] {
    return document.entities?.filter((entity) => entity.type === type) || [];
  }

  /**
   * Get FAQ by category
   */
  getFaqByCategory(document: AIIndexDocument, category?: string): any[] {
    if (!category) {
      return document.faq || [];
    }
    return document.faq?.filter((item) => item.category === category) || [];
  }
}
