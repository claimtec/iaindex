/**
 * Bubble.io Action: Verify Domain with AIIndex
 * Initiates and completes domain verification process
 */

function(properties, context) {
  const domain = properties.domain;
  const verificationMethod = properties.verification_method || 'dns';

  // Get API key from plugin settings
  const apiKey = context.keys['AIIndex API'];
  const apiEndpoint = 'https://api.aiindex.org/v1';

  if (!apiKey) {
    return {
      success: false,
      error: 'API key not configured',
      verification_status: 'error',
      verification_token: null,
      instructions: 'Please configure your AIIndex API key in plugin settings'
    };
  }

  if (!domain) {
    return {
      success: false,
      error: 'Domain is required',
      verification_status: 'error',
      verification_token: null,
      instructions: 'Please provide a domain to verify'
    };
  }

  try {
    // Request domain verification
    const response = fetch(`${apiEndpoint}/domains/verify`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'X-AIIndex-Plugin': 'Bubble/1.0.0'
      },
      body: JSON.stringify({
        domain: domain,
        verification_method: verificationMethod
      })
    });

    if (response.status === 200 || response.status === 201) {
      const result = JSON.parse(response.body);

      // Generate verification instructions based on method
      const instructions = generateVerificationInstructions(
        verificationMethod,
        result.verification_token,
        domain
      );

      // Save verification record to Bubble database
      saveVerificationRecord(result, domain, context);

      // If already verified, trigger event
      if (result.verification_status === 'verified') {
        context.trigger('Domain Verified', {
          domain: domain,
          verified_at: new Date().toISOString()
        });
      }

      return {
        success: true,
        verification_status: result.verification_status,
        verification_token: result.verification_token,
        instructions: instructions,
        expires_at: result.expires_at
      };
    } else {
      throw new Error(`Verification request failed: ${response.status}`);
    }

  } catch (error) {
    return {
      success: false,
      error: error.message,
      verification_status: 'error',
      verification_token: null,
      instructions: `Error: ${error.message}`
    };
  }
}

/**
 * Generate verification instructions based on method
 */
function generateVerificationInstructions(method, token, domain) {
  switch (method) {
    case 'dns':
      return `Add the following TXT record to your DNS settings:

Host: _aiindex.${domain}
Type: TXT
Value: aiindex-verification=${token}

After adding the record, click "Check Verification" to complete the process.`;

    case 'html':
      return `Create a file at the following location:

https://${domain}/.well-known/aiindex-verification.txt

With the following content:

${token}

After creating the file, click "Check Verification" to complete the process.`;

    case 'meta':
      return `Add the following meta tag to the <head> section of your homepage:

<meta name="aiindex-verification" content="${token}" />

After adding the tag, click "Check Verification" to complete the process.`;

    default:
      return 'Unknown verification method';
  }
}

/**
 * Save verification record to Bubble database
 */
function saveVerificationRecord(result, domain, context) {
  try {
    const verificationRecord = {
      type: 'Domain Verification',
      domain: domain,
      verification_token: result.verification_token,
      verification_status: result.verification_status,
      verification_method: result.verification_method,
      created_date: new Date(),
      expires_at: result.expires_at ? new Date(result.expires_at) : null
    };

    // Check if record exists
    const existing = context.database.search({
      type: 'Domain Verification',
      constraints: [{ field: 'domain', value: domain }]
    });

    if (existing.length > 0) {
      // Update existing record
      context.database.update(existing[0]._id, verificationRecord);
    } else {
      // Create new record
      context.database.create(verificationRecord);
    }
  } catch (error) {
    console.error('Failed to save verification record:', error);
  }
}
