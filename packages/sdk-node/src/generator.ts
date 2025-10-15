/**
 * AIIndexGenerator class for crawling websites and extracting metadata
 */

import axios from 'axios';
import * as cheerio from 'cheerio';
import type { AIIndexFile, AIIndexConfig, GeneratorOptions, CrawlOptions } from './types';

export class AIIndexGenerator {
  private baseUrl: string;
  private config: Partial<AIIndexConfig>;
  private crawlOptions: CrawlOptions;
  private visited: Set<string>;

  constructor(options: GeneratorOptions) {
    this.baseUrl = this.normalizeUrl(options.baseUrl);
    this.config = options.config || {};
    this.crawlOptions = {
      maxPages: 50,
      maxDepth: 3,
      followExternalLinks: false,
      timeout: 10000,
      userAgent: 'AIIndexBot/1.0',
      ...options.crawlOptions,
    };
    this.visited = new Set();
  }

  /**
   * Generate AIIndex file from website
   */
  public async generate(): Promise<AIIndexFile> {
    // Start crawling from base URL
    const metadata = await this.crawlUrl(this.baseUrl, 0);

    // Build AIIndex file
    const aiIndex: AIIndexFile = {
      version: this.config.version || '1.0',
      name: this.config.name || metadata.name || this.extractDomainName(this.baseUrl),
      description: this.config.description || metadata.description || '',
      url: this.config.url || this.baseUrl,
      capabilities: this.config.capabilities || metadata.capabilities || [],
      categories: this.config.categories || metadata.categories || [],
      contact: this.config.contact || metadata.contact,
      apiEndpoint: this.config.apiEndpoint || metadata.apiEndpoint,
      authentication: this.config.authentication,
      pricing: this.config.pricing,
      metadata: {
        ...metadata.additionalData,
        ...this.config.metadata,
        crawledPages: this.visited.size,
        crawledAt: new Date().toISOString(),
      },
      generated: new Date().toISOString(),
    };

    return aiIndex;
  }

  /**
   * Crawl a URL and extract metadata
   */
  private async crawlUrl(url: string, depth: number): Promise<any> {
    if (depth > (this.crawlOptions.maxDepth || 3)) {
      return {};
    }

    if (this.visited.size >= (this.crawlOptions.maxPages || 50)) {
      return {};
    }

    if (this.visited.has(url)) {
      return {};
    }

    this.visited.add(url);

    try {
      const response = await axios.get(url, {
        timeout: this.crawlOptions.timeout,
        headers: {
          'User-Agent': this.crawlOptions.userAgent || 'AIIndexBot/1.0',
        },
        validateStatus: (status) => status < 400,
      });

      const $ = cheerio.load(response.data);
      const metadata: any = {};

      // Extract basic metadata
      metadata.name = this.extractMetaTag($, 'og:site_name') ||
                      this.extractMetaTag($, 'application-name') ||
                      $('title').text().trim();

      metadata.description = this.extractMetaTag($, 'description') ||
                            this.extractMetaTag($, 'og:description') ||
                            this.extractMetaTag($, 'twitter:description');

      // Extract capabilities from keywords and content
      const keywords = this.extractMetaTag($, 'keywords');
      if (keywords) {
        metadata.capabilities = keywords.split(',').map(k => k.trim());
      }

      // Look for AI-related terms
      const bodyText = $('body').text().toLowerCase();
      const aiCapabilities = this.detectAICapabilities(bodyText);
      if (aiCapabilities.length > 0) {
        metadata.capabilities = [...(metadata.capabilities || []), ...aiCapabilities];
      }

      // Extract contact information
      const email = this.extractEmail($, bodyText);
      const contactUrl = this.extractMetaTag($, 'contact') ||
                        $('a[href*="contact"]').first().attr('href');

      if (email || contactUrl) {
        metadata.contact = {};
        if (email) metadata.contact.email = email;
        if (contactUrl) metadata.contact.url = this.resolveUrl(contactUrl);
      }

      // Look for API endpoint
      const apiLink = $('a[href*="api"], a[href*="docs/api"]').first().attr('href');
      if (apiLink) {
        metadata.apiEndpoint = this.resolveUrl(apiLink);
      }

      // Extract additional structured data
      metadata.additionalData = this.extractStructuredData($);

      // Crawl linked pages
      if (depth < (this.crawlOptions.maxDepth || 3)) {
        const links = this.extractLinks($);
        for (const link of links.slice(0, 5)) { // Limit sub-crawls
          const subMetadata = await this.crawlUrl(link, depth + 1);
          // Merge metadata
          if (subMetadata.capabilities) {
            metadata.capabilities = [...(metadata.capabilities || []), ...subMetadata.capabilities];
          }
        }
      }

      // Deduplicate capabilities
      if (metadata.capabilities) {
        metadata.capabilities = [...new Set(metadata.capabilities)];
      }

      return metadata;
    } catch (error) {
      console.error(`Error crawling ${url}:`, error);
      return {};
    }
  }

  /**
   * Extract meta tag content
   */
  private extractMetaTag($: cheerio.CheerioAPI, name: string): string | undefined {
    return $(`meta[name="${name}"]`).attr('content') ||
           $(`meta[property="${name}"]`).attr('content');
  }

  /**
   * Extract email from page
   */
  private extractEmail($: cheerio.CheerioAPI, text: string): string | undefined {
    // Try to find email in mailto links
    const mailtoLink = $('a[href^="mailto:"]').first().attr('href');
    if (mailtoLink) {
      return mailtoLink.replace('mailto:', '').split('?')[0];
    }

    // Try to find email in text using regex
    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/;
    const match = text.match(emailRegex);
    return match ? match[0] : undefined;
  }

  /**
   * Detect AI capabilities from text
   */
  private detectAICapabilities(text: string): string[] {
    const capabilities: string[] = [];
    const patterns = {
      'natural-language-processing': /\b(nlp|natural language|text analysis|sentiment analysis)\b/i,
      'machine-learning': /\b(machine learning|ml|predictive|classification)\b/i,
      'computer-vision': /\b(computer vision|image recognition|object detection)\b/i,
      'speech-recognition': /\b(speech recognition|voice|audio transcription)\b/i,
      'chatbot': /\b(chatbot|conversational|dialogue)\b/i,
      'recommendation': /\b(recommendation|personalization|suggest)\b/i,
      'translation': /\b(translation|multilingual|language translation)\b/i,
      'generation': /\b(generation|generative|gpt|llm)\b/i,
    };

    for (const [capability, pattern] of Object.entries(patterns)) {
      if (pattern.test(text)) {
        capabilities.push(capability);
      }
    }

    return capabilities;
  }

  /**
   * Extract structured data (JSON-LD, microdata)
   */
  private extractStructuredData($: cheerio.CheerioAPI): Record<string, any> {
    const data: Record<string, any> = {};

    // Extract JSON-LD
    $('script[type="application/ld+json"]').each((_, elem) => {
      try {
        const jsonLd = JSON.parse($(elem).html() || '{}');
        Object.assign(data, jsonLd);
      } catch {
        // Ignore parse errors
      }
    });

    return data;
  }

  /**
   * Extract links from page
   */
  private extractLinks($: cheerio.CheerioAPI): string[] {
    const links: string[] = [];
    $('a[href]').each((_, elem) => {
      const href = $(elem).attr('href');
      if (href) {
        const resolvedUrl = this.resolveUrl(href);
        if (this.shouldFollowLink(resolvedUrl)) {
          links.push(resolvedUrl);
        }
      }
    });
    return links;
  }

  /**
   * Check if link should be followed
   */
  private shouldFollowLink(url: string): boolean {
    try {
      const urlObj = new URL(url);
      const baseUrlObj = new URL(this.baseUrl);

      // Check if external
      if (urlObj.origin !== baseUrlObj.origin) {
        return this.crawlOptions.followExternalLinks || false;
      }

      // Check include/exclude patterns
      const pathname = urlObj.pathname;

      if (this.crawlOptions.excludePatterns) {
        for (const pattern of this.crawlOptions.excludePatterns) {
          if (new RegExp(pattern).test(pathname)) {
            return false;
          }
        }
      }

      if (this.crawlOptions.includePatterns) {
        for (const pattern of this.crawlOptions.includePatterns) {
          if (new RegExp(pattern).test(pathname)) {
            return true;
          }
        }
        return false;
      }

      return true;
    } catch {
      return false;
    }
  }

  /**
   * Resolve relative URL to absolute
   */
  private resolveUrl(url: string): string {
    try {
      return new URL(url, this.baseUrl).href;
    } catch {
      return url;
    }
  }

  /**
   * Normalize URL
   */
  private normalizeUrl(url: string): string {
    try {
      const urlObj = new URL(url);
      // Remove trailing slash
      return urlObj.href.replace(/\/$/, '');
    } catch {
      return url;
    }
  }

  /**
   * Extract domain name from URL
   */
  private extractDomainName(url: string): string {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname.replace(/^www\./, '');
    } catch {
      return 'Unknown';
    }
  }
}
