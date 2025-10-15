/**
 * Validator class for AIIndex file validation
 */

import type {
  AIIndexFile,
  AIIndexConfig,
  ValidationResult,
  ValidationError,
  ValidationWarning,
} from './types';

export class Validator {
  private static readonly REQUIRED_FIELDS = ['version', 'name', 'description', 'url', 'generated'];
  private static readonly SUPPORTED_VERSIONS = ['1.0', '1.0.0'];
  private static readonly URL_PATTERN = /^https?:\/\/.+/;
  private static readonly EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  /**
   * Validate an AIIndex file
   */
  public validate(data: Partial<AIIndexFile>): ValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    // Check required fields
    for (const field of Validator.REQUIRED_FIELDS) {
      if (!data[field as keyof AIIndexFile]) {
        errors.push({
          field,
          message: `Required field '${field}' is missing`,
          code: 'MISSING_REQUIRED_FIELD',
        });
      }
    }

    // Validate version
    if (data.version && !Validator.SUPPORTED_VERSIONS.includes(data.version)) {
      warnings.push({
        field: 'version',
        message: `Version '${data.version}' may not be supported. Supported versions: ${Validator.SUPPORTED_VERSIONS.join(', ')}`,
      });
    }

    // Validate URL
    if (data.url && !Validator.URL_PATTERN.test(data.url)) {
      errors.push({
        field: 'url',
        message: 'Invalid URL format. Must start with http:// or https://',
        code: 'INVALID_URL',
      });
    }

    // Validate name
    if (data.name && data.name.length < 3) {
      errors.push({
        field: 'name',
        message: 'Name must be at least 3 characters long',
        code: 'INVALID_NAME',
      });
    }

    // Validate description
    if (data.description && data.description.length < 10) {
      warnings.push({
        field: 'description',
        message: 'Description should be at least 10 characters for better discoverability',
      });
    }

    // Validate contact email
    if (data.contact?.email && !Validator.EMAIL_PATTERN.test(data.contact.email)) {
      errors.push({
        field: 'contact.email',
        message: 'Invalid email format',
        code: 'INVALID_EMAIL',
      });
    }

    // Validate contact URL
    if (data.contact?.url && !Validator.URL_PATTERN.test(data.contact.url)) {
      errors.push({
        field: 'contact.url',
        message: 'Invalid contact URL format',
        code: 'INVALID_URL',
      });
    }

    // Validate API endpoint
    if (data.apiEndpoint && !Validator.URL_PATTERN.test(data.apiEndpoint)) {
      errors.push({
        field: 'apiEndpoint',
        message: 'Invalid API endpoint URL format',
        code: 'INVALID_URL',
      });
    }

    // Validate capabilities
    if (data.capabilities && !Array.isArray(data.capabilities)) {
      errors.push({
        field: 'capabilities',
        message: 'Capabilities must be an array',
        code: 'INVALID_TYPE',
      });
    } else if (data.capabilities && data.capabilities.length === 0) {
      warnings.push({
        field: 'capabilities',
        message: 'Consider adding capabilities to improve discoverability',
      });
    }

    // Validate categories
    if (data.categories && !Array.isArray(data.categories)) {
      errors.push({
        field: 'categories',
        message: 'Categories must be an array',
        code: 'INVALID_TYPE',
      });
    }

    // Validate authentication type
    if (data.authentication?.type && !['none', 'api-key', 'oauth2'].includes(data.authentication.type)) {
      errors.push({
        field: 'authentication.type',
        message: "Authentication type must be 'none', 'api-key', or 'oauth2'",
        code: 'INVALID_VALUE',
      });
    }

    // Validate pricing model
    if (data.pricing?.model && !['free', 'subscription', 'pay-per-use'].includes(data.pricing.model)) {
      errors.push({
        field: 'pricing.model',
        message: "Pricing model must be 'free', 'subscription', or 'pay-per-use'",
        code: 'INVALID_VALUE',
      });
    }

    // Validate generated timestamp
    if (data.generated) {
      const timestamp = new Date(data.generated);
      if (isNaN(timestamp.getTime())) {
        errors.push({
          field: 'generated',
          message: 'Invalid timestamp format',
          code: 'INVALID_TIMESTAMP',
        });
      }
    }

    return {
      valid: errors.length === 0,
      errors: errors.length > 0 ? errors : undefined,
      warnings: warnings.length > 0 ? warnings : undefined,
    };
  }

  /**
   * Validate JSON schema structure
   */
  public validateSchema(json: string): ValidationResult {
    try {
      const data = JSON.parse(json);
      return this.validate(data);
    } catch (error) {
      return {
        valid: false,
        errors: [
          {
            field: 'root',
            message: error instanceof Error ? error.message : 'Invalid JSON format',
            code: 'INVALID_JSON',
          },
        ],
      };
    }
  }
}
