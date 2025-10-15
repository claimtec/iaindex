/**
 * SignatureManager class for cryptographic signing using ECDSA P-256
 */

import * as jose from 'jose';
import type { KeyPair, SignatureOptions, AIIndexFile } from './types';

export class SignatureManager {
  private privateKey?: jose.KeyLike;
  private publicKey?: jose.KeyLike;
  private algorithm: string;

  constructor(algorithm: 'ES256' | 'ES384' | 'ES512' = 'ES256') {
    this.algorithm = algorithm;
  }

  /**
   * Generate a new ECDSA key pair
   */
  public async generateKeyPair(options?: SignatureOptions): Promise<KeyPair> {
    const algorithm = options?.algorithm || 'ES256';
    const keyFormat = options?.keyFormat || 'jwk';

    // Determine the curve based on algorithm
    const curve = this.getCurveForAlgorithm(algorithm);

    // Generate key pair
    const { publicKey, privateKey } = await jose.generateKeyPair(algorithm, {
      extractable: true,
    });

    this.privateKey = privateKey;
    this.publicKey = publicKey;
    this.algorithm = algorithm;

    if (keyFormat === 'jwk') {
      const publicJwk = await jose.exportJWK(publicKey);
      const privateJwk = await jose.exportJWK(privateKey);

      return {
        publicKey: JSON.stringify(publicJwk, null, 2),
        privateKey: JSON.stringify(privateJwk, null, 2),
        algorithm,
      };
    } else {
      // PEM format
      const publicPem = await jose.exportSPKI(publicKey);
      const privatePem = await jose.exportPKCS8(privateKey);

      return {
        publicKey: publicPem,
        privateKey: privatePem,
        algorithm,
      };
    }
  }

  /**
   * Load private key from string
   */
  public async loadPrivateKey(privateKeyStr: string, algorithm?: 'ES256' | 'ES384' | 'ES512'): Promise<void> {
    try {
      // Try to parse as JWK first
      const jwk = JSON.parse(privateKeyStr);
      this.privateKey = await jose.importJWK(jwk, algorithm);
      this.algorithm = algorithm || jwk.alg || 'ES256';
    } catch {
      // Try as PEM
      this.privateKey = await jose.importPKCS8(privateKeyStr, algorithm || 'ES256');
      this.algorithm = algorithm || 'ES256';
    }
  }

  /**
   * Load public key from string
   */
  public async loadPublicKey(publicKeyStr: string, algorithm?: 'ES256' | 'ES384' | 'ES512'): Promise<void> {
    try {
      // Try to parse as JWK first
      const jwk = JSON.parse(publicKeyStr);
      this.publicKey = await jose.importJWK(jwk, algorithm);
      this.algorithm = algorithm || jwk.alg || 'ES256';
    } catch {
      // Try as PEM
      this.publicKey = await jose.importSPKI(publicKeyStr, algorithm || 'ES256');
      this.algorithm = algorithm || 'ES256';
    }
  }

  /**
   * Sign AIIndex data
   */
  public async sign(data: AIIndexFile): Promise<string> {
    if (!this.privateKey) {
      throw new Error('Private key not loaded. Call loadPrivateKey() or generateKeyPair() first.');
    }

    // Create a copy without signature fields
    const dataToSign = { ...data };
    delete dataToSign.signature;
    delete dataToSign.signedBy;

    // Create JWS (JSON Web Signature)
    const jws = await new jose.CompactSign(
      new TextEncoder().encode(JSON.stringify(dataToSign))
    )
      .setProtectedHeader({ alg: this.algorithm as 'ES256' | 'ES384' | 'ES512' })
      .sign(this.privateKey);

    return jws;
  }

  /**
   * Verify signature
   */
  public async verify(signedData: string, publicKeyStr?: string): Promise<boolean> {
    try {
      let publicKey = this.publicKey;

      if (publicKeyStr) {
        // Load provided public key
        try {
          const jwk = JSON.parse(publicKeyStr);
          publicKey = await jose.importJWK(jwk);
        } catch {
          publicKey = await jose.importSPKI(publicKeyStr, this.algorithm as 'ES256');
        }
      }

      if (!publicKey) {
        throw new Error('Public key not available. Provide publicKey or call loadPublicKey() first.');
      }

      // Verify JWS
      await jose.compactVerify(signedData, publicKey);
      return true;
    } catch (error) {
      console.error('Verification failed:', error);
      return false;
    }
  }

  /**
   * Add signature to AIIndex file
   */
  public async signFile(data: AIIndexFile): Promise<AIIndexFile> {
    if (!this.privateKey || !this.publicKey) {
      throw new Error('Keys not loaded. Call loadPrivateKey() and loadPublicKey() or generateKeyPair() first.');
    }

    const signature = await this.sign(data);
    const publicJwk = await jose.exportJWK(this.publicKey);

    return {
      ...data,
      signature,
      signedBy: {
        publicKey: JSON.stringify(publicJwk),
        algorithm: this.algorithm,
      },
    };
  }

  /**
   * Verify signed AIIndex file
   */
  public async verifyFile(data: AIIndexFile): Promise<boolean> {
    if (!data.signature || !data.signedBy?.publicKey) {
      throw new Error('File is not signed');
    }

    return this.verify(data.signature, data.signedBy.publicKey);
  }

  /**
   * Get curve name for algorithm
   */
  private getCurveForAlgorithm(algorithm: string): string {
    switch (algorithm) {
      case 'ES256':
        return 'P-256';
      case 'ES384':
        return 'P-384';
      case 'ES512':
        return 'P-521';
      default:
        return 'P-256';
    }
  }

  /**
   * Export public key as JWK string
   */
  public async exportPublicKey(): Promise<string> {
    if (!this.publicKey) {
      throw new Error('Public key not loaded');
    }
    const jwk = await jose.exportJWK(this.publicKey);
    return JSON.stringify(jwk, null, 2);
  }

  /**
   * Export private key as JWK string
   */
  public async exportPrivateKey(): Promise<string> {
    if (!this.privateKey) {
      throw new Error('Private key not loaded');
    }
    const jwk = await jose.exportJWK(this.privateKey);
    return JSON.stringify(jwk, null, 2);
  }
}
