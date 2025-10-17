/**
 * IAIndex Publisher Example - Complete Integration
 *
 * This example demonstrates:
 * 1. Domain verification
 * 2. Content indexing
 * 3. Receipt verification
 * 4. Analytics retrieval
 */

import 'dotenv/config';
import axios from 'axios';
import crypto from 'crypto';

const API_BASE_URL = process.env.API_BASE_URL || 'https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io';
const API_KEY = process.env.API_KEY || '';
const PUBLISHER_DOMAIN = process.env.PUBLISHER_DOMAIN || 'example.com';

// API client instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  }
});

/**
 * Step 1: Initiate domain verification
 */
async function initiateVerification() {
  console.log('\n=== Step 1: Initiating Domain Verification ===\n');

  try {
    const response = await api.post('/v1/publishers/verify', {
      domain: PUBLISHER_DOMAIN,
      method: 'dns_txt',
      contact_email: process.env.PUBLISHER_EMAIL
    });

    console.log('✓ Verification initiated successfully!');
    console.log('\nVerification Token:', response.data.verification_token);
    console.log('Status:', response.data.status);
    console.log('Expires At:', response.data.expires_at);
    console.log('\nInstructions:');
    console.log(response.data.instructions);

    return response.data;
  } catch (error) {
    console.error('✗ Verification initiation failed:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * Step 2: Check verification status
 */
async function checkVerification(token) {
  console.log('\n=== Step 2: Checking Verification Status ===\n');

  try {
    const response = await api.get(`/v1/publishers/verify/${token}`);

    console.log('Verification Status:', response.data.status);
    console.log('Verified:', response.data.verified);
    console.log('Message:', response.data.message);

    if (response.data.verified) {
      console.log('✓ Domain verified successfully!');
      console.log('Verified At:', response.data.verified_at);
    } else {
      console.log('⚠ Domain not yet verified. Please complete verification steps.');
    }

    return response.data;
  } catch (error) {
    console.error('✗ Verification check failed:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * Step 3: Generate AI-Index file
 */
function generateAIIndex() {
  console.log('\n=== Step 3: Generating AI-Index File ===\n');

  const aiIndex = {
    publisher: {
      domain: PUBLISHER_DOMAIN,
      name: process.env.PUBLISHER_NAME || 'Example Publisher',
      contact: process.env.PUBLISHER_EMAIL || 'contact@example.com',
      verified: true
    },
    entities: [
      {
        type: 'Organization',
        name: process.env.PUBLISHER_NAME || 'Example Publisher',
        description: 'An example publisher demonstrating IAIndex integration',
        url: `https://${PUBLISHER_DOMAIN}`
      }
    ],
    pages: [
      {
        url: `https://${PUBLISHER_DOMAIN}/article-1`,
        title: 'Introduction to IAIndex',
        description: 'Learn how IAIndex enables AI-readable web content',
        published_date: '2025-01-15',
        modified_date: '2025-01-15',
        author: 'Example Author',
        content_type: 'article',
        tags: ['ai', 'protocol', 'web']
      },
      {
        url: `https://${PUBLISHER_DOMAIN}/article-2`,
        title: 'Getting Started with IAIndex',
        description: 'A practical guide to implementing IAIndex on your website',
        published_date: '2025-01-16',
        modified_date: '2025-01-16',
        author: 'Example Author',
        content_type: 'tutorial',
        tags: ['tutorial', 'integration', 'guide']
      }
    ],
    faqs: [
      {
        question: 'What is IAIndex?',
        answer: 'IAIndex is an open protocol for AI-readable web content with cryptographic verification.'
      },
      {
        question: 'How do I get started?',
        answer: 'Install the SDK, verify your domain, and generate your AI-Index file.'
      }
    ],
    version: '1.0',
    generated_at: new Date().toISOString()
  };

  console.log('✓ AI-Index file generated:');
  console.log(JSON.stringify(aiIndex, null, 2));

  return aiIndex;
}

/**
 * Step 4: Submit a test receipt
 */
async function submitReceipt(articleUrl) {
  console.log('\n=== Step 4: Submitting Test Receipt ===\n');

  try {
    // Generate receipt data
    const receiptId = crypto.randomUUID();
    const timestamp = new Date().toISOString();

    // Create signature (simplified for demo - use proper signing in production)
    const signatureData = `${receiptId}:${PUBLISHER_DOMAIN}:${articleUrl}:${timestamp}`;
    const signature = crypto.createHmac('sha256', process.env.SECRET_KEY || 'demo-secret')
      .update(signatureData)
      .digest('hex');

    const receipt = {
      receipt_id: receiptId,
      publisher_domain: PUBLISHER_DOMAIN,
      article_url: articleUrl,
      timestamp: timestamp,
      signature: signature,
      metadata: {
        client: 'iaindex-example-client',
        version: '1.0.0'
      }
    };

    const response = await api.post('/v1/receipts/ingest', receipt);

    console.log('✓ Receipt submitted successfully!');
    console.log('Receipt ID:', response.data.receipt_id);
    console.log('Status:', response.data.status);
    console.log('Verified:', response.data.verified);
    console.log('Message:', response.data.message);

    return response.data;
  } catch (error) {
    console.error('✗ Receipt submission failed:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * Step 5: Get analytics
 */
async function getAnalytics() {
  console.log('\n=== Step 5: Retrieving Analytics ===\n');

  try {
    const response = await api.get('/v1/analytics', {
      params: {
        domain: PUBLISHER_DOMAIN,
        days: 30
      }
    });

    console.log('✓ Analytics retrieved successfully!');
    console.log('Domain:', response.data.domain);
    console.log('Total Receipts:', response.data.total_receipts);
    console.log('Verified Receipts:', response.data.verified_receipts);
    console.log('Failed Receipts:', response.data.failed_receipts);

    if (response.data.first_receipt_at) {
      console.log('First Receipt:', response.data.first_receipt_at);
    }
    if (response.data.last_receipt_at) {
      console.log('Last Receipt:', response.data.last_receipt_at);
    }

    if (response.data.daily_breakdown) {
      console.log('\nDaily Breakdown:');
      Object.entries(response.data.daily_breakdown).forEach(([date, count]) => {
        console.log(`  ${date}: ${count} receipts`);
      });
    }

    return response.data;
  } catch (error) {
    console.error('✗ Analytics retrieval failed:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * Step 6: List verified domains
 */
async function listVerifiedDomains() {
  console.log('\n=== Step 6: Listing Verified Domains ===\n');

  try {
    const response = await api.get('/v1/publishers/verified-domains');

    console.log('✓ Retrieved verified domains!');
    console.log('Total Verified Domains:', response.data.total);
    console.log('\nDomains:');

    response.data.domains.forEach(domain => {
      console.log(`  - ${domain.domain}`);
      console.log(`    Verified: ${domain.verified_at}`);
      console.log(`    Receipts: ${domain.receipt_count}`);
      if (domain.last_receipt_at) {
        console.log(`    Last Receipt: ${domain.last_receipt_at}`);
      }
    });

    return response.data;
  } catch (error) {
    console.error('✗ Failed to retrieve verified domains:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * Main execution
 */
async function main() {
  console.log('╔════════════════════════════════════════════╗');
  console.log('║  IAIndex Publisher Integration Example    ║');
  console.log('╚════════════════════════════════════════════╝');

  if (!API_KEY) {
    console.error('\n✗ Error: API_KEY not set in environment variables');
    console.error('Please copy .env.example to .env and configure your settings\n');
    process.exit(1);
  }

  try {
    // Step 1: Initiate verification
    const verificationData = await initiateVerification();

    // Step 2: Check verification status
    // In a real scenario, wait for DNS propagation before checking
    console.log('\n⚠ Note: In production, wait for DNS propagation before checking verification');
    console.log('For this demo, we\'ll continue to other steps...\n');

    // Step 3: Generate AI-Index
    const aiIndex = generateAIIndex();

    // Step 4: Submit test receipt (assuming domain is verified)
    const testArticleUrl = `https://${PUBLISHER_DOMAIN}/article-1`;
    // Uncomment after domain verification:
    // await submitReceipt(testArticleUrl);

    // Step 5: Get analytics
    // await getAnalytics();

    // Step 6: List verified domains
    await listVerifiedDomains();

    console.log('\n╔════════════════════════════════════════════╗');
    console.log('║  Integration Complete!                     ║');
    console.log('╚════════════════════════════════════════════╝\n');

    console.log('Next Steps:');
    console.log('1. Complete domain verification (add DNS TXT record)');
    console.log('2. Check verification: npm run verify');
    console.log('3. Deploy ai-index.json to your website root');
    console.log('4. Test receipt submission');
    console.log('5. Monitor analytics in dashboard\n');

  } catch (error) {
    console.error('\n✗ Integration failed:', error.message);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { initiateVerification, checkVerification, generateAIIndex, submitReceipt, getAnalytics, listVerifiedDomains };
