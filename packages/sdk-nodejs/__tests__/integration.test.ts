/**
 * Integration tests against live API
 */

import { IAIndexPublisher, IAIndexClient, CryptoUtils } from '../src';

const API_BASE_URL = 'https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io';

describe('IAIndex SDK Integration Tests', () => {
  let publisherKeyPair: any;
  let clientKeyPair: any;

  beforeAll(() => {
    // Generate test key pairs
    publisherKeyPair = CryptoUtils.generateKeyPair();
    clientKeyPair = CryptoUtils.generateKeyPair();
  });

  describe('IAIndexPublisher', () => {
    let publisher: IAIndexPublisher;

    beforeEach(() => {
      publisher = new IAIndexPublisher({
        domain: 'example.com',
        privateKey: publisherKeyPair.privateKey,
        name: 'Example Publication',
        contact: 'publisher@example.com',
        apiBaseUrl: API_BASE_URL,
      });
    });

    it('should initialize publisher', async () => {
      await expect(publisher.initialize()).resolves.not.toThrow();
    });

    it('should add content entry', async () => {
      const entry = {
        url: 'https://example.com/article-1',
        title: 'Test Article',
        author: 'Test Author',
        publishedDate: new Date().toISOString(),
        license: { type: 'CC-BY-4.0' },
      };

      const entryId = await publisher.addEntry(entry);
      expect(typeof entryId).toBe('string');
      expect(entryId.length).toBeGreaterThan(0);
    });

    it('should generate index file', async () => {
      await publisher.initialize();

      const entry = {
        url: 'https://example.com/article-2',
        title: 'Another Test Article',
        author: 'Test Author',
        publishedDate: new Date().toISOString(),
        license: { type: 'MIT' },
      };

      await publisher.addEntry(entry);

      const index = await publisher.generateIndex();

      expect(index).toHaveProperty('domain', 'example.com');
      expect(index).toHaveProperty('publisher');
      expect(index.publisher).toHaveProperty('name', 'Example Publication');
      expect(index).toHaveProperty('entries');
      expect(Array.isArray(index.entries)).toBe(true);
      expect(index.entries.length).toBeGreaterThan(0);
      expect(index).toHaveProperty('signature');
      expect(index).toHaveProperty('timestamp');
      expect(index).toHaveProperty('version');
    });

    it('should validate entry fields', async () => {
      await publisher.initialize();

      const invalidEntry = {
        url: 'https://example.com/invalid',
        title: 'Test',
        // Missing author, publishedDate, and license
      } as any;

      await expect(publisher.addEntry(invalidEntry)).rejects.toThrow();
    });

    it('should verify receipt', async () => {
      const receipt = {
        receiptId: CryptoUtils.generateId(),
        publisherDomain: 'example.com',
        articleUrl: 'https://example.com/article',
        timestamp: new Date().toISOString(),
        signature: '',
      };

      // Sign the receipt
      const receiptData = {
        receiptId: receipt.receiptId,
        publisherDomain: receipt.publisherDomain,
        articleUrl: receipt.articleUrl,
        timestamp: receipt.timestamp,
      };
      receipt.signature = CryptoUtils.sign(receiptData, publisherKeyPair.privateKey);

      const isValid = await publisher.verifyReceipt(receipt);
      expect(isValid).toBe(true);
    });
  });

  describe('IAIndexClient', () => {
    let client: IAIndexClient;

    beforeEach(() => {
      client = new IAIndexClient({
        clientId: 'test-client-123',
        privateKey: clientKeyPair.privateKey,
        name: 'Test AI Client',
        organization: 'Test Org',
        apiBaseUrl: API_BASE_URL,
      });
    });

    it('should initialize client', async () => {
      await expect(client.initialize()).resolves.not.toThrow();
    });

    it('should access content and get metadata', async () => {
      const url = 'https://example.com';

      const metadata = await client.accessContent(url);

      expect(metadata).toHaveProperty('url', url);
      expect(metadata).toBeDefined();
    });

    it('should send usage receipt', async () => {
      await client.initialize();

      const content = {
        url: 'https://example.com/article',
        title: 'Test Article',
        author: 'Test Author',
      };

      const usage = {
        purpose: 'training' as const,
        context: 'language-model-pretraining',
        modelId: 'test-model-v1',
      };

      const result = await client.sendReceipt(content, usage);
      expect(typeof result).toBe('boolean');
    });

    it('should validate usage purpose', async () => {
      await client.initialize();

      const content = {
        url: 'https://example.com/article',
      };

      const invalidUsage = {
        purpose: 'invalid-purpose' as any,
        context: 'test',
      };

      await expect(client.sendReceipt(content, invalidUsage)).resolves.toBe(false);
    });

    it('should get verified publishers', async () => {
      await client.initialize();

      const publishers = await client.getVerifiedPublishers();

      expect(Array.isArray(publishers)).toBe(true);
    });
  });

  describe('End-to-End Workflow', () => {
    it('should complete full publisher-to-client workflow', async () => {
      // 1. Publisher publishes content
      const publisher = new IAIndexPublisher({
        domain: 'testpublisher.com',
        privateKey: publisherKeyPair.privateKey,
        name: 'Test Publisher',
        contact: 'test@testpublisher.com',
        apiBaseUrl: API_BASE_URL,
      });

      await publisher.initialize();

      const contentEntry = {
        url: 'https://testpublisher.com/article',
        title: 'E2E Test Article',
        author: 'E2E Test Author',
        publishedDate: new Date().toISOString(),
        content: 'This is a test article for end-to-end testing.',
        license: { type: 'CC-BY-4.0', terms: 'Attribution required' },
      };

      const entryId = await publisher.addEntry(contentEntry);
      expect(entryId).toBeDefined();

      // 2. Generate and verify index
      const index = await publisher.generateIndex();
      expect(index.entries).toContainEqual(expect.objectContaining({
        url: contentEntry.url,
        title: contentEntry.title,
      }));

      // 3. AI Client accesses content
      const client = new IAIndexClient({
        clientId: 'e2e-test-client',
        privateKey: clientKeyPair.privateKey,
        name: 'E2E Test Client',
        organization: 'E2E Test Org',
        apiBaseUrl: API_BASE_URL,
      });

      await client.initialize();

      const metadata = await client.accessContent(contentEntry.url);
      expect(metadata.url).toBe(contentEntry.url);

      // 4. Client sends usage receipt
      const receiptSent = await client.sendReceipt(metadata, {
        purpose: 'training',
        context: 'e2e-testing',
        modelId: 'e2e-test-model',
      });

      expect(receiptSent).toBe(true);
    });
  });
});
