/**
 * Cryptographic utilities for signing and verification
 */

import * as crypto from 'crypto';
import * as elliptic from 'elliptic';
import { KeyPair } from './types';

const EC = elliptic.ec;
const ec = new EC('secp256k1');

export class CryptoUtils {
  /**
   * Generate a new ECDSA key pair
   */
  static generateKeyPair(): KeyPair {
    const keyPair = ec.genKeyPair();
    return {
      privateKey: keyPair.getPrivate('hex'),
      publicKey: keyPair.getPublic('hex'),
    };
  }

  /**
   * Sign data with a private key using ECDSA
   */
  static sign(data: string | object, privateKey: string): string {
    const dataString = typeof data === 'string' ? data : JSON.stringify(data);
    const hash = crypto.createHash('sha256').update(dataString).digest();

    const keyPair = ec.keyFromPrivate(privateKey, 'hex');
    const signature = keyPair.sign(hash);

    return signature.toDER('hex');
  }

  /**
   * Verify a signature using a public key
   */
  static verify(data: string | object, signature: string, publicKey: string): boolean {
    try {
      const dataString = typeof data === 'string' ? data : JSON.stringify(data);
      const hash = crypto.createHash('sha256').update(dataString).digest();

      const key = ec.keyFromPublic(publicKey, 'hex');
      return key.verify(hash, signature);
    } catch (error) {
      return false;
    }
  }

  /**
   * Get public key from private key
   */
  static getPublicKey(privateKey: string): string {
    const keyPair = ec.keyFromPrivate(privateKey, 'hex');
    return keyPair.getPublic('hex');
  }

  /**
   * Generate a hash of data
   */
  static hash(data: string | object): string {
    const dataString = typeof data === 'string' ? data : JSON.stringify(data);
    return crypto.createHash('sha256').update(dataString).digest('hex');
  }

  /**
   * Generate a random ID
   */
  static generateId(): string {
    return crypto.randomBytes(16).toString('hex');
  }

  /**
   * Create HMAC signature for API requests
   */
  static createHmac(data: string, secret: string): string {
    return crypto.createHmac('sha256', secret).update(data).digest('hex');
  }

  /**
   * Verify HMAC signature
   */
  static verifyHmac(data: string, signature: string, secret: string): boolean {
    const expectedSignature = this.createHmac(data, secret);
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature)
    );
  }
}
