/**
 * IAIndexClient - For AI clients to access content and send usage receipts
 */

import { APIClient } from './api-client';
import { CryptoUtils } from './crypto';
import { ClientOptions, ContentMetadata, UsageInfo, Receipt } from './types';
import axios from 'axios';

const DEFAULT_API_URL = 'https://api.iaindex.org';

export class IAIndexClient {
  private apiClient: APIClient;
  private clientId: string;
  private privateKey: string;
  private publicKey: string;
  private name?: string;
  private organization?: string;
  private initialized: boolean = false;

  constructor(options: ClientOptions) {
    this.clientId = options.clientId;
    this.privateKey = options.privateKey;
    this.name = options.name;
    this.organization = options.organization;

    // Derive public key from private key
    this.publicKey = CryptoUtils.getPublicKey(this.privateKey);

    // Initialize API client
    const apiBaseUrl = options.apiBaseUrl || DEFAULT_API_URL;
    this.apiClient = new APIClient(apiBaseUrl);
  }

  /**
   * Initialize client and authenticate with API
   */
  async initialize(): Promise<void> {
    try {
      // Authenticate with the API
      await this.apiClient.authenticate();
      this.initialized = true;
    } catch (error: any) {
      throw new Error(`Failed to initialize client: ${error.message}`);
    }
  }

  /**
   * Access content and retrieve metadata
   */
  async accessContent(url: string): Promise<ContentMetadata> {
    if (!this.initialized) {
      await this.initialize();
    }

    try {
      // First, try to fetch the actual content
      let metadata: ContentMetadata = { url };

      try {
        const response = await axios.get(url, {
          timeout: 10000,
          headers: {
            'User-Agent': `IAIndexClient/${this.clientId}`,
          },
        });

        // Extract basic metadata from HTML if possible
        const html = response.data;
        metadata = this.extractMetadata(html, url);
      } catch (error) {
        // If content fetch fails, just use the URL
        console.warn(`Could not fetch content from ${url}`);
      }

      // Try to get publisher information from API
      try {
        const publishers = await this.apiClient.get('/v1/publishers/verified-domains');

        // Find publisher by domain
        const urlDomain = new URL(url).hostname.replace('www.', '');
        const publisher = publishers.domains?.find((p: any) =>
          p.domain === urlDomain || url.includes(p.domain)
        );

        if (publisher) {
          metadata.publisher = {
            domain: publisher.domain,
            name: publisher.domain,
          };
        }
      } catch (error) {
        // Publisher info not available
      }

      return metadata;
    } catch (error: any) {
      throw new Error(`Failed to access content: ${error.message}`);
    }
  }

  /**
   * Extract metadata from HTML content
   */
  private extractMetadata(html: string, url: string): ContentMetadata {
    const metadata: ContentMetadata = { url };

    // Extract title from <title> tag
    const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
    if (titleMatch) {
      metadata.title = titleMatch[1].trim();
    }

    // Extract author from meta tags
    const authorMatch = html.match(/<meta[^>]*name=["']author["'][^>]*content=["']([^"']+)["']/i);
    if (authorMatch) {
      metadata.author = authorMatch[1].trim();
    }

    // Extract published date from meta tags
    const dateMatch = html.match(/<meta[^>]*property=["']article:published_time["'][^>]*content=["']([^"']+)["']/i);
    if (dateMatch) {
      metadata.publishedDate = dateMatch[1].trim();
    }

    return metadata;
  }

  /**
   * Send usage receipt for accessed content
   */
  async sendReceipt(content: ContentMetadata, usage: UsageInfo): Promise<boolean> {
    if (!this.initialized) {
      await this.initialize();
    }

    try {
      // Validate usage info
      this.validateUsage(usage);

      // Create receipt
      const receipt = this.createUsageReceipt(content, usage);

      // Submit receipt to API
      await this.submitReceipt(receipt);

      return true;
    } catch (error: any) {
      console.error(`Failed to send receipt: ${error.message}`);
      return false;
    }
  }

  /**
   * Validate usage information
   */
  private validateUsage(usage: UsageInfo): void {
    const validPurposes = ['training', 'inference', 'research'];
    if (!validPurposes.includes(usage.purpose)) {
      throw new Error(`Invalid usage purpose. Must be one of: ${validPurposes.join(', ')}`);
    }

    if (!usage.context || typeof usage.context !== 'string') {
      throw new Error('Usage context is required');
    }
  }

  /**
   * Create usage receipt
   */
  private createUsageReceipt(content: ContentMetadata, usage: UsageInfo): Receipt {
    const receiptId = CryptoUtils.generateId();
    const timestamp = new Date().toISOString();

    // Get publisher domain from content
    let publisherDomain = 'unknown';
    if (content.publisher?.domain) {
      publisherDomain = content.publisher.domain;
    } else {
      try {
        publisherDomain = new URL(content.url).hostname.replace('www.', '');
      } catch (error) {
        // Use unknown if URL parsing fails
      }
    }

    const receiptData = {
      receiptId,
      publisherDomain,
      articleUrl: content.url,
      timestamp,
    };

    // Sign the receipt
    const signature = CryptoUtils.sign(receiptData, this.privateKey);

    return {
      receiptId,
      publisherDomain,
      articleUrl: content.url,
      timestamp,
      signature,
      metadata: {
        clientId: this.clientId,
        clientName: this.name,
        organization: this.organization,
        usage: {
          purpose: usage.purpose,
          context: usage.context,
          datasetId: usage.datasetId,
          modelId: usage.modelId,
        },
        content: {
          title: content.title,
          author: content.author,
          publishedDate: content.publishedDate,
        },
      },
    };
  }

  /**
   * Submit receipt to API
   */
  private async submitReceipt(receipt: Receipt): Promise<void> {
    try {
      await this.apiClient.post('/v1/receipts/ingest', {
        receipt_id: receipt.receiptId,
        publisher_domain: receipt.publisherDomain,
        article_url: receipt.articleUrl,
        timestamp: receipt.timestamp,
        signature: receipt.signature,
        metadata: receipt.metadata,
      });
    } catch (error: any) {
      throw new Error(`Failed to submit receipt: ${error.response?.data?.error || error.message}`);
    }
  }

  /**
   * Get verified publishers
   */
  async getVerifiedPublishers(): Promise<any[]> {
    if (!this.initialized) {
      await this.initialize();
    }

    try {
      const response = await this.apiClient.get('/v1/publishers/verified-domains');
      return response.domains || [];
    } catch (error: any) {
      throw new Error(`Failed to get verified publishers: ${error.message}`);
    }
  }

  /**
   * Get client ID
   */
  getClientId(): string {
    return this.clientId;
  }

  /**
   * Get public key
   */
  getPublicKey(): string {
    return this.publicKey;
  }
}
