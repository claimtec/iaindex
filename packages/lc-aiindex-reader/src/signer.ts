/**
 * AIIndexReceiptSigner - Create and sign access receipts, post to publisher webhooks
 */

import * as jose from 'jose';
import axios, { AxiosInstance, AxiosError } from 'axios';
import { v4 as uuidv4 } from 'uuid';
import * as crypto from 'crypto';
import type {
  AIIndexDocument,
  Receipt,
  ReceiptSignerOptions,
  Signature,
  Access,
  Purpose,
  Attribution,
  AIIndexPolicy,
} from './types';

export class AIIndexReceiptSigner {
  private options: Required<ReceiptSignerOptions>;
  private client: AxiosInstance;
  private privateKey?: jose.KeyLike;

  constructor(options: ReceiptSignerOptions) {
    this.options = {
      clientId: options.clientId,
      clientName: options.clientName || 'LangChain AIIndex Client',
      clientVersion: options.clientVersion || '1.0.0',
      privateKeyPem: options.privateKeyPem,
      keyId: options.keyId,
      algorithm: options.algorithm || 'ES256',
      webhookRetries: options.webhookRetries || 3,
      webhookTimeout: options.webhookTimeout || 10000,
      intent: options.intent || 'retrieval',
    };

    this.client = axios.create({
      timeout: this.options.webhookTimeout,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': `${this.options.clientName}/${this.options.clientVersion}`,
        'X-AIIndex-Version': 'v1.1',
        'X-AIIndex-Client-ID': this.options.clientId,
        'X-AIIndex-Intent': this.options.intent,
      },
    });
  }

  /**
   * Initialize by loading the private key
   */
  async initialize(): Promise<void> {
    try {
      // Try to parse as JWK first
      const jwk = JSON.parse(this.options.privateKeyPem);
      this.privateKey = await jose.importJWK(jwk, this.options.algorithm);
    } catch {
      // Try as PEM
      this.privateKey = await jose.importPKCS8(
        this.options.privateKeyPem,
        this.options.algorithm
      );
    }
  }

  /**
   * Create and sign a receipt for accessing an ai-index.json file
   */
  async createReceipt(
    document: AIIndexDocument,
    options: {
      url: string;
      statusCode?: number;
      pagesAccessed?: string[];
      purpose?: Purpose;
      attribution?: Attribution;
      metadata?: Record<string, any>;
    }
  ): Promise<Receipt> {
    if (!this.privateKey) {
      await this.initialize();
    }

    const receiptId = uuidv4();
    const timestamp = new Date().toISOString();

    // Compute content hash
    const contentHash = this.computeHash(JSON.stringify(document));

    // Build access details
    const access: Access = {
      url: options.url,
      method: 'GET',
      status_code: options.statusCode || 200,
      content_hash: contentHash,
      pages_accessed: options.pagesAccessed,
    };

    // Build receipt payload (without signature)
    const payload: Omit<Receipt, 'signature'> = {
      version: '1.0',
      receipt_id: receiptId,
      publisher_id: document.publisher_id,
      publisher_domain: document.domain,
      client_id: this.options.clientId,
      client_name: this.options.clientName,
      client_version: this.options.clientVersion,
      timestamp,
      access,
      purpose: options.purpose,
      attribution: options.attribution,
      metadata: {
        user_agent: `${this.options.clientName}/${this.options.clientVersion}`,
        sdk_version: '1.0.0',
        ...options.metadata,
      },
    };

    // Sign the payload
    const signature = await this.signPayload(payload);

    // Create complete receipt
    const receipt: Receipt = {
      ...payload,
      signature,
    };

    return receipt;
  }

  /**
   * Sign receipt payload
   */
  private async signPayload(payload: any): Promise<Signature> {
    if (!this.privateKey) {
      throw new Error('Private key not loaded. Call initialize() first.');
    }

    // Serialize payload
    const payloadJson = JSON.stringify(payload, null, 0);
    const payloadBytes = new TextEncoder().encode(payloadJson);

    // Compute hash
    const payloadHash = this.computeHash(payloadJson);

    // Create JWS (JSON Web Signature)
    const jws = await new jose.CompactSign(payloadBytes)
      .setProtectedHeader({ alg: this.options.algorithm })
      .sign(this.privateKey);

    return {
      algorithm: this.options.algorithm,
      kid: this.options.keyId,
      signature: jws,
      document_hash: payloadHash,
      signed_at: new Date().toISOString(),
    };
  }

  /**
   * Post receipt to publisher's webhook
   */
  async postReceipt(receipt: Receipt, webhookUrl: string, intent?: 'training' | 'retrieval'): Promise<boolean> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < this.options.webhookRetries; attempt++) {
      try {
        const headers: Record<string, string> = {
          'X-AIIndex-Version': 'v1.1',
          'X-AIIndex-Client-ID': this.options.clientId,
          'X-AIIndex-Intent': intent || this.options.intent || 'retrieval',
        };

        const response = await this.client.post(webhookUrl, receipt, { headers });

        if (response.status >= 200 && response.status < 300) {
          return true;
        }

        throw new Error(`Webhook returned status ${response.status}`);
      } catch (error) {
        lastError = error as Error;
        console.error(`Failed to post receipt (attempt ${attempt + 1}/${this.options.webhookRetries}):`, error);

        if (attempt < this.options.webhookRetries - 1) {
          // Exponential backoff
          const delay = Math.pow(2, attempt) * 1000;
          await new Promise((resolve) => setTimeout(resolve, delay));
        }
      }
    }

    console.error('All webhook retry attempts failed:', lastError);
    return false;
  }

  /**
   * Create receipt and automatically post to webhook if specified
   */
  async createAndPostReceipt(
    document: AIIndexDocument,
    options: {
      url: string;
      statusCode?: number;
      pagesAccessed?: string[];
      purpose?: Purpose;
      attribution?: Attribution;
      metadata?: Record<string, any>;
      webhookUrl?: string;
      intent?: 'training' | 'retrieval';
    }
  ): Promise<{ receipt: Receipt; posted: boolean }> {
    const receipt = await this.createReceipt(document, options);

    let posted = false;
    const webhookUrl = options.webhookUrl || document.access_policy?.webhook_url;
    if (webhookUrl) {
      posted = await this.postReceipt(receipt, webhookUrl, options.intent);
    }

    return { receipt, posted };
  }

  /**
   * Batch create and post receipts
   */
  async createAndPostReceiptsBatch(
    items: Array<{
      document: AIIndexDocument;
      options: {
        url: string;
        statusCode?: number;
        pagesAccessed?: string[];
        purpose?: Purpose;
        attribution?: Attribution;
        metadata?: Record<string, any>;
      };
    }>
  ): Promise<Array<{ receipt: Receipt; posted: boolean; error?: string }>> {
    const results = await Promise.allSettled(
      items.map((item) => this.createAndPostReceipt(item.document, item.options))
    );

    return results.map((result, index) => {
      if (result.status === 'fulfilled') {
        return result.value;
      } else {
        return {
          receipt: {} as Receipt,
          posted: false,
          error: result.reason?.message || 'Unknown error',
        };
      }
    });
  }

  /**
   * Generate a new keypair for signing
   */
  static async generateKeyPair(algorithm: 'ES256' | 'RS256' = 'ES256'): Promise<{
    privateKey: string;
    publicKey: string;
  }> {
    const { publicKey, privateKey } = await jose.generateKeyPair(algorithm, {
      extractable: true,
    });

    const privateJwk = await jose.exportJWK(privateKey);
    const publicJwk = await jose.exportJWK(publicKey);

    return {
      privateKey: JSON.stringify(privateJwk, null, 2),
      publicKey: JSON.stringify(publicJwk, null, 2),
    };
  }

  /**
   * Verify a receipt signature
   */
  static async verifyReceipt(receipt: Receipt, publicKeyJwk: string): Promise<boolean> {
    try {
      const jwk = JSON.parse(publicKeyJwk);
      const publicKey = await jose.importJWK(jwk);

      // Remove signature from payload
      const { signature, ...payload } = receipt;

      // Serialize payload
      const payloadJson = JSON.stringify(payload, null, 0);

      // Verify JWS
      await jose.compactVerify(signature.signature, publicKey);

      // Verify hash
      const computedHash = crypto
        .createHash('sha256')
        .update(payloadJson)
        .digest('hex');

      return computedHash === signature.document_hash;
    } catch (error) {
      console.error('Receipt verification failed:', error);
      return false;
    }
  }

  /**
   * Compute SHA-256 hash
   */
  private computeHash(data: string): string {
    return crypto.createHash('sha256').update(data).digest('hex');
  }
}
