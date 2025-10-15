#!/usr/bin/env node
/**
 * Custom AIIndex Crawler
 *
 * This example demonstrates a custom crawler that:
 * 1. Discovers AIIndex-enabled websites
 * 2. Respects access policies
 * 3. Sends access receipts
 * 4. Handles rate limiting
 * 5. Stores indexed content
 *
 * Usage:
 *   node custom-crawler.js [domains...]
 *
 * Requirements:
 *   npm install axios cheerio bottleneck
 */

const axios = require('axios');
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');
const Bottleneck = require('bottleneck');
const fs = require('fs').promises;
const path = require('path');

/**
 * AIIndex Crawler with rate limiting and receipt handling
 */
class AIIndexCrawler {
  constructor(options = {}) {
    this.clientId = options.clientId || 'custom-crawler';
    this.clientName = options.clientName || 'Custom AIIndex Crawler';
    this.userAgent = options.userAgent || 'AIIndexCrawler/1.0';
    this.outputDir = options.outputDir || './crawled-data';
    this.respectRateLimit = options.respectRateLimit !== false;

    // Rate limiter: 1 request per second per domain
    this.limiter = new Bottleneck({
      minTime: 1000,
      maxConcurrent: 1,
    });

    // Storage for crawled data
    this.indexedSites = new Map();
  }

  /**
   * Discover if a domain has AIIndex
   */
  async discoverAIIndex(domain) {
    const aiIndexUrl = `https://${domain}/.well-known/ai-index.json`;

    try {
      console.log(`🔍 Checking ${domain} for AIIndex...`);

      const response = await axios.get(aiIndexUrl, {
        headers: { 'User-Agent': this.userAgent },
        timeout: 10000,
      });

      console.log(`✓ Found AIIndex at ${domain}`);
      return {
        found: true,
        url: aiIndexUrl,
        data: response.data,
      };
    } catch (error) {
      if (error.response?.status === 404) {
        console.log(`✗ No AIIndex found at ${domain}`);
      } else {
        console.error(`✗ Error checking ${domain}: ${error.message}`);
      }
      return { found: false };
    }
  }

  /**
   * Check if access is allowed
   */
  isAccessAllowed(aiIndex) {
    const policy = aiIndex.access_policy;

    if (!policy) return true;

    if (policy.allowed === false) {
      console.log(`⚠ Access not allowed for ${aiIndex.domain}`);
      return false;
    }

    return true;
  }

  /**
   * Crawl a single domain
   */
  async crawlDomain(domain) {
    // Discover AIIndex
    const discovery = await this.discoverAIIndex(domain);

    if (!discovery.found) {
      return null;
    }

    const aiIndex = discovery.data;

    // Check access policy
    if (!this.isAccessAllowed(aiIndex)) {
      return null;
    }

    console.log(`\n📄 Crawling ${aiIndex.publisher?.name || domain}...`);
    console.log(`   Pages: ${aiIndex.pages?.length || 0}`);
    console.log(`   Receipt required: ${aiIndex.access_policy?.receipt_required || false}`);
    console.log(`   Attribution required: ${aiIndex.access_policy?.attribution_required || false}`);

    // Extract page information
    const pages = aiIndex.pages || [];
    const crawledPages = pages.map(page => ({
      url: page.url,
      title: page.title,
      description: page.description,
      summary: page.summary,
      content_type: page.content_type,
      tags: page.tags || [],
    }));

    // Store indexed data
    const siteData = {
      domain: aiIndex.domain,
      publisher: aiIndex.publisher,
      pages: crawledPages,
      access_policy: aiIndex.access_policy,
      crawled_at: new Date().toISOString(),
    };

    this.indexedSites.set(domain, siteData);

    // Send receipt if required
    if (aiIndex.access_policy?.receipt_required) {
      await this.sendReceipt(aiIndex, crawledPages.map(p => p.url));
    }

    // Save to file
    await this.saveSiteData(domain, siteData);

    console.log(`✓ Crawled ${domain}: ${crawledPages.length} pages indexed`);

    return siteData;
  }

  /**
   * Send access receipt
   */
  async sendReceipt(aiIndex, pagesAccessed) {
    const webhookUrl = aiIndex.access_policy?.webhook_url;

    if (!webhookUrl) {
      console.log('⚠ Receipt required but no webhook URL provided');
      return;
    }

    const receipt = {
      version: '1.0',
      receipt_id: uuidv4(),
      publisher_id: aiIndex.publisher_id,
      publisher_domain: aiIndex.domain,
      client_id: this.clientId,
      client_name: this.clientName,
      timestamp: new Date().toISOString(),
      access: {
        url: `https://${aiIndex.domain}/.well-known/ai-index.json`,
        method: 'GET',
        status_code: 200,
        content_hash: this.generateHash(JSON.stringify(aiIndex)),
        pages_accessed: pagesAccessed.slice(0, 10), // Include first 10 pages
      },
      purpose: {
        type: 'indexing',
        description: 'Building search index from public content',
        commercial: false, // Adjust based on your use case
      },
      attribution: {
        method: 'citation',
        citation_text: `Content indexed from ${aiIndex.publisher?.name || aiIndex.domain}`,
      },
      metadata: {
        user_agent: this.userAgent,
        crawler_version: '1.0.0',
      },
    };

    try {
      await axios.post(webhookUrl, receipt, {
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': this.userAgent,
        },
        timeout: 5000,
      });
      console.log(`✓ Receipt sent to ${aiIndex.domain}`);
    } catch (error) {
      console.error(`✗ Failed to send receipt: ${error.message}`);
    }
  }

  /**
   * Generate content hash
   */
  generateHash(content) {
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  /**
   * Save site data to file
   */
  async saveSiteData(domain, data) {
    try {
      await fs.mkdir(this.outputDir, { recursive: true });

      const filename = path.join(this.outputDir, `${domain.replace(/[^a-z0-9]/gi, '_')}.json`);
      await fs.writeFile(filename, JSON.stringify(data, null, 2));

      console.log(`💾 Saved data to ${filename}`);
    } catch (error) {
      console.error(`✗ Failed to save data: ${error.message}`);
    }
  }

  /**
   * Crawl multiple domains
   */
  async crawlMultiple(domains) {
    console.log(`\n🚀 Starting crawl of ${domains.length} domains...\n`);

    const results = [];

    for (const domain of domains) {
      try {
        // Apply rate limiting
        const result = await this.limiter.schedule(() => this.crawlDomain(domain));
        if (result) {
          results.push(result);
        }
      } catch (error) {
        console.error(`✗ Error crawling ${domain}: ${error.message}`);
      }

      // Add delay between domains
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Generate summary
    await this.generateSummary(results);

    return results;
  }

  /**
   * Generate crawl summary
   */
  async generateSummary(results) {
    const summary = {
      total_sites: results.length,
      total_pages: results.reduce((sum, site) => sum + site.pages.length, 0),
      sites_by_policy: {
        receipt_required: results.filter(s => s.access_policy?.receipt_required).length,
        attribution_required: results.filter(s => s.access_policy?.attribution_required).length,
        commercial_allowed: results.filter(s => s.access_policy?.commercial_use !== false).length,
      },
      content_types: {},
      crawled_at: new Date().toISOString(),
    };

    // Count content types
    results.forEach(site => {
      site.pages.forEach(page => {
        const type = page.content_type || 'unknown';
        summary.content_types[type] = (summary.content_types[type] || 0) + 1;
      });
    });

    // Save summary
    const summaryPath = path.join(this.outputDir, 'crawl-summary.json');
    await fs.writeFile(summaryPath, JSON.stringify(summary, null, 2));

    console.log('\n📊 Crawl Summary:');
    console.log(`   Total sites: ${summary.total_sites}`);
    console.log(`   Total pages: ${summary.total_pages}`);
    console.log(`   Sites requiring receipts: ${summary.sites_by_policy.receipt_required}`);
    console.log(`   Sites requiring attribution: ${summary.sites_by_policy.attribution_required}`);
    console.log(`   Content types:`, summary.content_types);
    console.log(`\n💾 Summary saved to ${summaryPath}`);
  }

  /**
   * Search indexed content
   */
  searchIndexed(query) {
    const results = [];
    const lowerQuery = query.toLowerCase();

    for (const [domain, siteData] of this.indexedSites) {
      siteData.pages.forEach(page => {
        const matchScore = this.calculateMatchScore(page, lowerQuery);
        if (matchScore > 0) {
          results.push({
            ...page,
            domain,
            publisher: siteData.publisher?.name || domain,
            score: matchScore,
          });
        }
      });
    }

    // Sort by score
    results.sort((a, b) => b.score - a.score);

    return results;
  }

  /**
   * Calculate match score for search
   */
  calculateMatchScore(page, query) {
    let score = 0;

    const searchText = [
      page.title,
      page.description,
      page.summary,
      ...(page.tags || []),
    ].join(' ').toLowerCase();

    // Check for query matches
    if (searchText.includes(query)) {
      score += 10;
    }

    // Boost for title matches
    if (page.title?.toLowerCase().includes(query)) {
      score += 20;
    }

    // Boost for tag matches
    if (page.tags?.some(tag => tag.toLowerCase().includes(query))) {
      score += 15;
    }

    return score;
  }
}

/**
 * Example usage
 */
async function main() {
  const domains = process.argv.slice(2);

  if (domains.length === 0) {
    console.log('Usage: node custom-crawler.js [domains...]');
    console.log('\nExample:');
    console.log('  node custom-crawler.js example-blog.com techgear-shop.com cloudforge-docs.dev');
    process.exit(1);
  }

  const crawler = new AIIndexCrawler({
    clientId: 'my-custom-crawler',
    clientName: 'My Custom Crawler',
    outputDir: './crawled-data',
  });

  // Crawl domains
  const results = await crawler.crawlMultiple(domains);

  // Example search
  if (results.length > 0) {
    console.log('\n\n🔍 Example Search: "ai agents"');
    const searchResults = crawler.searchIndexed('ai agents');

    console.log(`\nFound ${searchResults.length} results:\n`);
    searchResults.slice(0, 5).forEach((result, i) => {
      console.log(`${i + 1}. ${result.title}`);
      console.log(`   Publisher: ${result.publisher}`);
      console.log(`   URL: ${result.url}`);
      console.log(`   Score: ${result.score}`);
      console.log();
    });
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { AIIndexCrawler };
