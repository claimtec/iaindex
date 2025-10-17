/**
 * IAIndex Webflow Snippet
 * Version: 1.0.0
 *
 * Automatically generates and maintains AI-Index data for Webflow sites.
 * Tracks content access and sends cryptographic receipts to IAIndex.
 *
 * Installation:
 * 1. Add this script to Webflow Project Settings > Custom Code > Head Code
 * 2. Configure the settings below
 * 3. Publish your site
 *
 * Features:
 * - Automatic page indexing
 * - Content metadata extraction
 * - Receipt generation for AI access tracking
 * - Lightweight and non-blocking
 */

(function() {
  'use strict';

  // ============================================================================
  // CONFIGURATION - Edit these settings
  // ============================================================================

  const IAINDEX_CONFIG = {
    // Your IAIndex API key
    apiKey: 'YOUR_API_KEY_HERE',

    // Your domain (auto-detected if not set)
    domain: window.location.hostname,

    // Publisher information
    publisher: {
      name: 'Your Site Name',
      contact: 'contact@yourdomain.com'
    },

    // IAIndex API endpoint
    apiEndpoint: 'https://aiindex-api.calmmeadow-49a6bfdb.eastus.azurecontainerapps.io',

    // Enable/disable features
    features: {
      autoIndex: true,        // Automatically index pages
      trackAccess: true,      // Track AI access
      generateReceipts: true, // Generate receipts for AI clients
      debug: false            // Enable debug logging
    },

    // Content selectors for metadata extraction
    selectors: {
      title: 'h1, .page-title, .post-title',
      description: '.page-description, .post-excerpt, meta[name="description"]',
      author: '.author-name, .post-author, meta[name="author"]',
      publishDate: '.publish-date, .post-date, time[datetime]',
      content: 'article, .main-content, .post-content',
      tags: '.tag, .category, .post-tag'
    }
  };

  // ============================================================================
  // DO NOT EDIT BELOW THIS LINE (unless you know what you're doing)
  // ============================================================================

  // Debug logger
  const log = (...args) => {
    if (IAINDEX_CONFIG.features.debug) {
      console.log('[IAIndex]', ...args);
    }
  };

  // ============================================================================
  // Metadata Extraction
  // ============================================================================

  function extractPageMetadata() {
    log('Extracting page metadata...');

    const metadata = {
      url: window.location.href,
      title: extractTitle(),
      description: extractDescription(),
      author: extractAuthor(),
      publishDate: extractPublishDate(),
      modifiedDate: extractModifiedDate(),
      contentType: detectContentType(),
      tags: extractTags(),
      wordCount: estimateWordCount(),
      language: document.documentElement.lang || 'en'
    };

    log('Extracted metadata:', metadata);
    return metadata;
  }

  function extractTitle() {
    // Try selectors first
    const titleElement = document.querySelector(IAINDEX_CONFIG.selectors.title);
    if (titleElement) return titleElement.textContent.trim();

    // Fallback to document title
    return document.title;
  }

  function extractDescription() {
    // Try selector
    const descElement = document.querySelector(IAINDEX_CONFIG.selectors.description);
    if (descElement) {
      if (descElement.tagName === 'META') {
        return descElement.getAttribute('content');
      }
      return descElement.textContent.trim();
    }

    // Fallback to meta description
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) return metaDesc.getAttribute('content');

    // Fallback to first paragraph
    const firstPara = document.querySelector('p');
    if (firstPara) return firstPara.textContent.trim().substring(0, 200);

    return '';
  }

  function extractAuthor() {
    // Try selector
    const authorElement = document.querySelector(IAINDEX_CONFIG.selectors.author);
    if (authorElement) {
      if (authorElement.tagName === 'META') {
        return authorElement.getAttribute('content');
      }
      return authorElement.textContent.trim();
    }

    // Fallback to meta author
    const metaAuthor = document.querySelector('meta[name="author"]');
    if (metaAuthor) return metaAuthor.getAttribute('content');

    return null;
  }

  function extractPublishDate() {
    // Try selector
    const dateElement = document.querySelector(IAINDEX_CONFIG.selectors.publishDate);
    if (dateElement) {
      const datetime = dateElement.getAttribute('datetime');
      if (datetime) return datetime;
      return dateElement.textContent.trim();
    }

    // Try meta tags
    const metaPublished = document.querySelector('meta[property="article:published_time"]');
    if (metaPublished) return metaPublished.getAttribute('content');

    return null;
  }

  function extractModifiedDate() {
    const metaModified = document.querySelector('meta[property="article:modified_time"]');
    if (metaModified) return metaModified.getAttribute('content');

    return new Date().toISOString();
  }

  function extractTags() {
    const tagElements = document.querySelectorAll(IAINDEX_CONFIG.selectors.tags);
    const tags = Array.from(tagElements).map(el => el.textContent.trim());

    // Also check meta keywords
    const metaKeywords = document.querySelector('meta[name="keywords"]');
    if (metaKeywords) {
      const keywords = metaKeywords.getAttribute('content').split(',').map(k => k.trim());
      tags.push(...keywords);
    }

    return [...new Set(tags)]; // Remove duplicates
  }

  function detectContentType() {
    const path = window.location.pathname;

    if (path.includes('/blog/') || path.includes('/post/')) return 'blog-post';
    if (path.includes('/article/')) return 'article';
    if (path.includes('/news/')) return 'news';
    if (path.includes('/product/')) return 'product';
    if (path === '/' || path === '') return 'homepage';

    // Check for article tag
    if (document.querySelector('article')) return 'article';

    return 'page';
  }

  function estimateWordCount() {
    const contentElement = document.querySelector(IAINDEX_CONFIG.selectors.content);
    if (!contentElement) return 0;

    const text = contentElement.textContent || '';
    const words = text.trim().split(/\s+/);
    return words.length;
  }

  // ============================================================================
  // AI-Index Generation
  // ============================================================================

  function generateAIIndex() {
    log('Generating AI-Index data...');

    const metadata = extractPageMetadata();

    const aiIndex = {
      publisher: {
        domain: IAINDEX_CONFIG.domain,
        name: IAINDEX_CONFIG.publisher.name,
        contact: IAINDEX_CONFIG.publisher.contact,
        verified: true
      },
      pages: [
        {
          url: metadata.url,
          title: metadata.title,
          description: metadata.description,
          published_date: metadata.publishDate,
          modified_date: metadata.modifiedDate,
          author: metadata.author,
          content_type: metadata.contentType,
          tags: metadata.tags,
          word_count: metadata.wordCount,
          language: metadata.language
        }
      ],
      version: '1.0',
      generated_at: new Date().toISOString(),
      generator: 'iaindex-webflow-snippet-v1.0.0'
    };

    return aiIndex;
  }

  // ============================================================================
  // Receipt Tracking
  // ============================================================================

  function detectAIAccess() {
    // Check for AI bot user agents
    const userAgent = navigator.userAgent.toLowerCase();
    const aiBots = [
      'gptbot',
      'chatgpt',
      'claudebot',
      'anthropic',
      'bingbot',
      'googlebot-ai',
      'perplexitybot'
    ];

    return aiBots.some(bot => userAgent.includes(bot));
  }

  async function generateReceipt() {
    if (!IAINDEX_CONFIG.features.generateReceipts) return;
    if (!detectAIAccess()) return;

    log('AI access detected, generating receipt...');

    try {
      const receiptId = generateUUID();
      const timestamp = new Date().toISOString();

      const receipt = {
        receipt_id: receiptId,
        publisher_domain: IAINDEX_CONFIG.domain,
        article_url: window.location.href,
        timestamp: timestamp,
        signature: await generateSignature(receiptId, timestamp),
        metadata: {
          user_agent: navigator.userAgent,
          referrer: document.referrer,
          page_title: document.title,
          generator: 'webflow-snippet'
        }
      };

      await sendReceipt(receipt);
    } catch (error) {
      log('Receipt generation failed:', error);
    }
  }

  async function generateSignature(receiptId, timestamp) {
    // For client-side, we use a simple hash
    // In production, signature should be generated server-side
    const data = `${receiptId}:${IAINDEX_CONFIG.domain}:${window.location.href}:${timestamp}`;
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  async function sendReceipt(receipt) {
    log('Sending receipt to IAIndex...', receipt);

    try {
      const response = await fetch(`${IAINDEX_CONFIG.apiEndpoint}/v1/receipts/ingest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': IAINDEX_CONFIG.apiKey
        },
        body: JSON.stringify(receipt)
      });

      if (response.ok) {
        const data = await response.json();
        log('Receipt sent successfully:', data);
      } else {
        log('Receipt submission failed:', response.status, await response.text());
      }
    } catch (error) {
      log('Receipt submission error:', error);
    }
  }

  // ============================================================================
  // Utilities
  // ============================================================================

  function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  // ============================================================================
  // Page Index Metadata Tag
  // ============================================================================

  function injectMetadata() {
    if (!IAINDEX_CONFIG.features.autoIndex) return;

    log('Injecting IAIndex metadata...');

    const aiIndex = generateAIIndex();

    // Add JSON-LD script tag
    const scriptTag = document.createElement('script');
    scriptTag.type = 'application/ld+json';
    scriptTag.setAttribute('data-iaindex', 'true');
    scriptTag.textContent = JSON.stringify(aiIndex, null, 2);

    document.head.appendChild(scriptTag);

    // Add meta tag for verification
    const metaTag = document.createElement('meta');
    metaTag.setAttribute('name', 'iaindex:page');
    metaTag.setAttribute('content', 'indexed');

    document.head.appendChild(metaTag);

    log('Metadata injected successfully');
  }

  // ============================================================================
  // Initialization
  // ============================================================================

  function init() {
    log('IAIndex Webflow Snippet initialized');
    log('Configuration:', IAINDEX_CONFIG);

    // Check if API key is set
    if (IAINDEX_CONFIG.apiKey === 'YOUR_API_KEY_HERE') {
      console.warn('[IAIndex] API key not configured. Please set your API key in the snippet configuration.');
      return;
    }

    // Inject page metadata
    injectMetadata();

    // Track AI access
    if (IAINDEX_CONFIG.features.trackAccess) {
      generateReceipt();
    }

    // Expose API for manual control
    window.IAIndex = {
      config: IAINDEX_CONFIG,
      extractMetadata: extractPageMetadata,
      generateIndex: generateAIIndex,
      sendReceipt: generateReceipt,
      version: '1.0.0'
    };

    log('IAIndex API exposed on window.IAIndex');
  }

  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
