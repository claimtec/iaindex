/**
 * ReceiptHandler class for receiving and forwarding receipts to AIIndex API
 */

import axios, { AxiosInstance } from 'axios';
import * as http from 'http';
import type { Receipt, ReceiptHandlerOptions, WebhookServerOptions } from './types';

export class ReceiptHandler {
  private apiClient: AxiosInstance;
  private options: ReceiptHandlerOptions;
  private server?: http.Server;

  constructor(options: ReceiptHandlerOptions) {
    this.options = {
      autoForward: true,
      retryAttempts: 3,
      retryDelay: 1000,
      ...options,
    };

    this.apiClient = axios.create({
      baseURL: this.options.apiEndpoint,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        ...(this.options.apiKey && { 'Authorization': `Bearer ${this.options.apiKey}` }),
      },
    });
  }

  /**
   * Forward receipt to AIIndex API
   */
  public async forwardReceipt(receipt: Receipt): Promise<boolean> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < (this.options.retryAttempts || 3); attempt++) {
      try {
        await this.apiClient.post('/receipts', receipt);
        return true;
      } catch (error) {
        lastError = error as Error;
        console.error(`Failed to forward receipt (attempt ${attempt + 1}):`, error);

        if (attempt < (this.options.retryAttempts || 3) - 1) {
          // Wait before retry
          await new Promise(resolve =>
            setTimeout(resolve, this.options.retryDelay || 1000)
          );
        }
      }
    }

    console.error('All retry attempts failed:', lastError);
    return false;
  }

  /**
   * Batch forward multiple receipts
   */
  public async forwardReceiptsBatch(receipts: Receipt[]): Promise<{ success: number; failed: number }> {
    const results = await Promise.allSettled(
      receipts.map(receipt => this.forwardReceipt(receipt))
    );

    const success = results.filter(r => r.status === 'fulfilled' && r.value).length;
    const failed = results.length - success;

    return { success, failed };
  }

  /**
   * Start webhook server to receive receipts
   */
  public async startWebhookServer(options: WebhookServerOptions = {}): Promise<http.Server> {
    const port = options.port || 3000;
    const path = options.path || '/webhook/receipts';
    const apiKey = options.apiKey;

    this.server = http.createServer(async (req, res) => {
      // CORS headers
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

      if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
      }

      if (req.method !== 'POST' || req.url !== path) {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Not found' }));
        return;
      }

      // Verify API key if provided
      if (apiKey) {
        const authHeader = req.headers.authorization;
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
          res.writeHead(401, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Unauthorized' }));
          return;
        }

        const token = authHeader.substring(7);
        if (token !== apiKey) {
          res.writeHead(403, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Forbidden' }));
          return;
        }
      }

      // Parse request body
      let body = '';
      req.on('data', chunk => {
        body += chunk.toString();
      });

      req.on('end', async () => {
        try {
          const receipt: Receipt = JSON.parse(body);

          // Validate receipt
          if (!this.validateReceipt(receipt)) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Invalid receipt format' }));
            return;
          }

          // Call custom handler if provided
          if (options.onReceipt) {
            await options.onReceipt(receipt);
          }

          // Auto-forward if enabled
          if (this.options.autoForward) {
            await this.forwardReceipt(receipt);
          }

          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: true, receiptId: receipt.id }));
        } catch (error) {
          console.error('Error processing receipt:', error);
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Internal server error' }));
        }
      });
    });

    return new Promise((resolve, reject) => {
      this.server!.listen(port, () => {
        console.log(`Webhook server listening on port ${port}`);
        console.log(`Endpoint: http://localhost:${port}${path}`);
        resolve(this.server!);
      });

      this.server!.on('error', reject);
    });
  }

  /**
   * Stop webhook server
   */
  public async stopWebhookServer(): Promise<void> {
    if (!this.server) {
      return;
    }

    return new Promise((resolve, reject) => {
      this.server!.close((error) => {
        if (error) {
          reject(error);
        } else {
          console.log('Webhook server stopped');
          resolve();
        }
      });
    });
  }

  /**
   * Validate receipt format
   */
  private validateReceipt(receipt: any): receipt is Receipt {
    return (
      typeof receipt === 'object' &&
      typeof receipt.id === 'string' &&
      typeof receipt.agentId === 'string' &&
      typeof receipt.timestamp === 'string' &&
      typeof receipt.action === 'string' &&
      ['view', 'click', 'interaction'].includes(receipt.action)
    );
  }

  /**
   * Create a receipt object
   */
  public static createReceipt(
    agentId: string,
    action: 'view' | 'click' | 'interaction',
    metadata?: Record<string, any>
  ): Receipt {
    return {
      id: this.generateReceiptId(),
      agentId,
      timestamp: new Date().toISOString(),
      action,
      metadata,
    };
  }

  /**
   * Generate unique receipt ID
   */
  private static generateReceiptId(): string {
    return `rcpt_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  }
}
