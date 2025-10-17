/**
 * Tests for cryptographic utilities
 */

import { CryptoUtils } from '../src/crypto';

describe('CryptoUtils', () => {
  describe('generateKeyPair', () => {
    it('should generate a valid key pair', () => {
      const keyPair = CryptoUtils.generateKeyPair();

      expect(keyPair).toHaveProperty('privateKey');
      expect(keyPair).toHaveProperty('publicKey');
      expect(typeof keyPair.privateKey).toBe('string');
      expect(typeof keyPair.publicKey).toBe('string');
      expect(keyPair.privateKey.length).toBeGreaterThan(0);
      expect(keyPair.publicKey.length).toBeGreaterThan(0);
    });

    it('should generate unique key pairs', () => {
      const keyPair1 = CryptoUtils.generateKeyPair();
      const keyPair2 = CryptoUtils.generateKeyPair();

      expect(keyPair1.privateKey).not.toBe(keyPair2.privateKey);
      expect(keyPair1.publicKey).not.toBe(keyPair2.publicKey);
    });
  });

  describe('sign and verify', () => {
    const keyPair = CryptoUtils.generateKeyPair();
    const testData = { message: 'Hello, World!' };

    it('should sign data correctly', () => {
      const signature = CryptoUtils.sign(testData, keyPair.privateKey);

      expect(typeof signature).toBe('string');
      expect(signature.length).toBeGreaterThan(0);
    });

    it('should verify valid signature', () => {
      const signature = CryptoUtils.sign(testData, keyPair.privateKey);
      const isValid = CryptoUtils.verify(testData, signature, keyPair.publicKey);

      expect(isValid).toBe(true);
    });

    it('should reject invalid signature', () => {
      const signature = CryptoUtils.sign(testData, keyPair.privateKey);
      const tamperedData = { message: 'Tampered message' };
      const isValid = CryptoUtils.verify(tamperedData, signature, keyPair.publicKey);

      expect(isValid).toBe(false);
    });

    it('should reject signature with wrong public key', () => {
      const otherKeyPair = CryptoUtils.generateKeyPair();
      const signature = CryptoUtils.sign(testData, keyPair.privateKey);
      const isValid = CryptoUtils.verify(testData, signature, otherKeyPair.publicKey);

      expect(isValid).toBe(false);
    });
  });

  describe('getPublicKey', () => {
    it('should derive public key from private key', () => {
      const keyPair = CryptoUtils.generateKeyPair();
      const derivedPublicKey = CryptoUtils.getPublicKey(keyPair.privateKey);

      expect(derivedPublicKey).toBe(keyPair.publicKey);
    });
  });

  describe('hash', () => {
    it('should hash string data', () => {
      const data = 'test data';
      const hash = CryptoUtils.hash(data);

      expect(typeof hash).toBe('string');
      expect(hash.length).toBe(64); // SHA-256 hex = 64 chars
    });

    it('should hash object data', () => {
      const data = { key: 'value' };
      const hash = CryptoUtils.hash(data);

      expect(typeof hash).toBe('string');
      expect(hash.length).toBe(64);
    });

    it('should produce consistent hashes', () => {
      const data = { key: 'value' };
      const hash1 = CryptoUtils.hash(data);
      const hash2 = CryptoUtils.hash(data);

      expect(hash1).toBe(hash2);
    });

    it('should produce different hashes for different data', () => {
      const data1 = { key: 'value1' };
      const data2 = { key: 'value2' };
      const hash1 = CryptoUtils.hash(data1);
      const hash2 = CryptoUtils.hash(data2);

      expect(hash1).not.toBe(hash2);
    });
  });

  describe('generateId', () => {
    it('should generate a random ID', () => {
      const id = CryptoUtils.generateId();

      expect(typeof id).toBe('string');
      expect(id.length).toBe(32); // 16 bytes * 2 (hex)
    });

    it('should generate unique IDs', () => {
      const id1 = CryptoUtils.generateId();
      const id2 = CryptoUtils.generateId();

      expect(id1).not.toBe(id2);
    });
  });

  describe('HMAC operations', () => {
    const secret = 'test-secret';
    const data = 'test data';

    it('should create HMAC signature', () => {
      const hmac = CryptoUtils.createHmac(data, secret);

      expect(typeof hmac).toBe('string');
      expect(hmac.length).toBe(64); // SHA-256 hex
    });

    it('should verify valid HMAC', () => {
      const hmac = CryptoUtils.createHmac(data, secret);
      const isValid = CryptoUtils.verifyHmac(data, hmac, secret);

      expect(isValid).toBe(true);
    });

    it('should reject invalid HMAC', () => {
      const hmac = CryptoUtils.createHmac(data, secret);
      const isValid = CryptoUtils.verifyHmac('tampered data', hmac, secret);

      expect(isValid).toBe(false);
    });

    it('should reject HMAC with wrong secret', () => {
      const hmac = CryptoUtils.createHmac(data, secret);
      const isValid = CryptoUtils.verifyHmac(data, hmac, 'wrong-secret');

      expect(isValid).toBe(false);
    });
  });
});
