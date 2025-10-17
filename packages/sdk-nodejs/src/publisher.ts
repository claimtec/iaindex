/**
 * IAIndexPublisher - For content publishers to register and verify content
 */

import { APIClient } from './api-client';
import { CryptoUtils } from './crypto';
import { PublisherOptions, ContentEntry, IndexFile, Receipt } from './types';

const DEFAULT_API_URL = 'https://api.iaindex.org';

export class IAIndexPublisher {
  private apiClient: APIClient;
  private domain: string;
  private privateKey: string;
  private publicKey: string;
  private name: string;
  private contact: string;
  private entries: ContentEntry[] = [];
  private initialized: boolean = false;

  constructor(options: PublisherOptions) {
    this.domain = options.domain;
    this.privateKey = options.privateKey;
    this.name = options.name;
    this.contact = options.contact;

    // Derive public key from private key
    this.publicKey = CryptoUtils.getPublicKey(this.privateKey);

    // Initialize API client
    const apiBaseUrl = options.apiBaseUrl || DEFAULT_API_URL;
    this.apiClient = new APIClient(apiBaseUrl);
  }

  /**
   * Initialize publisher profile and authenticate with API
   */
  async initialize(): Promise<void> {
    try {
      // Authenticate with the API
      await this.apiClient.authenticate();

      // Verify domain (initiate verification if not already verified)
      try {
        await this.verifyDomain();
      } catch (error: any) {
        // If domain verification fails, continue but log warning
        console.warn(`Domain verification not completed: ${error.message}`);
      }

      this.initialized = true;
    } catch (error: any) {
      throw new Error(`Failed to initialize publisher: ${error.message}`);
    }
  }

  /**
   * Initiate domain verification
   */
  private async verifyDomain(): Promise<void> {
    try {
      const response = await this.apiClient.post('/v1/publishers/verify', {
        domain: this.domain,
        method: 'dns_txt',
      });

      if (response.status === 'verified') {
        return;
      }

      // Log verification instructions
      console.log('Domain verification required:');
      console.log(response.instructions);
    } catch (error: any) {
      // If domain is already verified, that's fine
      if (error.response?.status !== 409) {
        throw error;
      }
    }
  }

  /**
   * Add a content entry to the index
   */
  async addEntry(entry: ContentEntry): Promise<string> {
    if (!this.initialized) {
      await this.initialize();
    }

    // Validate entry
    this.validateEntry(entry);

    // Add to local entries
    this.entries.push(entry);

    // Generate entry ID
    const entryId = CryptoUtils.hash({
      url: entry.url,
      domain: this.domain,
      timestamp: new Date().toISOString(),
    });

    // Create receipt for this entry
    const receipt = await this.createReceipt(entry);

    // Submit receipt to API
    try {
      await this.submitReceipt(receipt);
    } catch (error: any) {
      console.warn(`Failed to submit receipt: ${error.message}`);
    }

    return entryId;
  }

  /**
   * Validate content entry
   */
  private validateEntry(entry: ContentEntry): void {
    if (!entry.url || typeof entry.url !== 'string') {
      throw new Error('Entry must have a valid URL');
    }
    if (!entry.title || typeof entry.title !== 'string') {
      throw new Error('Entry must have a title');
    }
    if (!entry.author || typeof entry.author !== 'string') {
      throw new Error('Entry must have an author');
    }
    if (!entry.publishedDate || typeof entry.publishedDate !== 'string') {
      throw new Error('Entry must have a published date');
    }
    if (!entry.license || !entry.license.type) {
      throw new Error('Entry must have a license type');
    }
  }

  /**
   * Create a receipt for a content entry
   */
  private async createReceipt(entry: ContentEntry): Promise<Receipt> {
    const receiptId = CryptoUtils.generateId();
    const timestamp = new Date().toISOString();

    const receiptData = {
      receiptId,
      publisherDomain: this.domain,
      articleUrl: entry.url,
      timestamp,
    };

    // Sign the receipt
    const signature = CryptoUtils.sign(receiptData, this.privateKey);

    return {
      receiptId,
      publisherDomain: this.domain,
      articleUrl: entry.url,
      timestamp,
      signature,
      metadata: {
        title: entry.title,
        author: entry.author,
        publishedDate: entry.publishedDate,
        license: entry.license,
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
   * Generate signed index file with all entries
   */
  async generateIndex(): Promise<IndexFile> {
    if (!this.initialized) {
      await this.initialize();
    }

    const timestamp = new Date().toISOString();

    const indexData = {
      domain: this.domain,
      publisher: {
        name: this.name,
        contact: this.contact,
      },
      entries: this.entries,
      timestamp,
      version: '1.0',
    };

    // Sign the index
    const signature = CryptoUtils.sign(indexData, this.privateKey);

    return {
      ...indexData,
      signature,
    };
  }

  /**
   * Verify a receipt signature
   */
  async verifyReceipt(receipt: Receipt): Promise<boolean> {
    try {
      const receiptData = {
        receiptId: receipt.receiptId,
        publisherDomain: receipt.publisherDomain,
        articleUrl: receipt.articleUrl,
        timestamp: receipt.timestamp,
      };

      return CryptoUtils.verify(receiptData, receipt.signature, this.publicKey);
    } catch (error) {
      return false;
    }
  }

  /**
   * Get all entries
   */
  getEntries(): ContentEntry[] {
    return [...this.entries];
  }

  /**
   * Get public key
   */
  getPublicKey(): string {
    return this.publicKey;
  }

  /**
   * Get domain
   */
  getDomain(): string {
    return this.domain;
  }
}
