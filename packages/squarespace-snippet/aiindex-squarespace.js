/**
 * AI Index Integration for Squarespace
 *
 * This script automatically generates and publishes an AI-readable index
 * of your Squarespace site content for AI search engines like ChatGPT,
 * Perplexity, and Claude.
 *
 * Installation: Add this script to Settings > Advanced > Code Injection > Header
 *
 * @version 1.0.0
 * @author ClaimTec
 */

(function() {
  'use strict';

  // Configuration (will be set via config UI)
  const AI_INDEX_CONFIG = {
    apiKey: localStorage.getItem('aiindex_api_key') || '',
    webhookUrl: localStorage.getItem('aiindex_webhook_url') || '',
    autoPublish: localStorage.getItem('aiindex_auto_publish') !== 'false',
    includePages: localStorage.getItem('aiindex_include_pages') !== 'false',
    includeBlog: localStorage.getItem('aiindex_include_blog') !== 'false',
    includeProducts: localStorage.getItem('aiindex_include_products') === 'true',
    apiBaseUrl: 'https://api.aiindex.com/v1'
  };

  /**
   * AI Index Generator Class
   */
  class AIIndexGenerator {
    constructor(config) {
      this.config = config;
      this.aiIndex = {
        version: '1.0',
        metadata: {
          site_name: '',
          base_url: window.location.origin,
          last_updated: new Date().toISOString(),
          language: document.documentElement.lang || 'en',
          contact: {}
        },
        pages: []
      };
    }

    /**
     * Initialize and gather site metadata
     */
    async init() {
      // Get site name from title or meta
      this.aiIndex.metadata.site_name = document.title.split('—')[0].trim() ||
                                         document.title.split('|')[0].trim() ||
                                         document.title;

      // Get contact info from meta tags
      const emailMeta = document.querySelector('meta[property="og:email"], meta[name="contact:email"]');
      if (emailMeta) {
        this.aiIndex.metadata.contact.email = emailMeta.content;
      }

      // Get site description
      const descMeta = document.querySelector('meta[name="description"], meta[property="og:description"]');
      if (descMeta) {
        this.aiIndex.metadata.description = descMeta.content;
      }
    }

    /**
     * Fetch all pages using Squarespace's navigation and sitemap
     */
    async fetchPages() {
      if (!this.config.includePages) return;

      const pages = [];

      // Method 1: Parse navigation
      const navLinks = document.querySelectorAll('nav a[href^="/"]');
      navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && !href.includes('#') && !href.includes('?')) {
          pages.push({
            url: window.location.origin + href,
            title: link.textContent.trim()
          });
        }
      });

      // Method 2: Try to fetch sitemap
      try {
        const sitemapResponse = await fetch('/sitemap.xml');
        if (sitemapResponse.ok) {
          const sitemapText = await sitemapResponse.text();
          const parser = new DOMParser();
          const xmlDoc = parser.parseFromString(sitemapText, 'text/xml');
          const urlElements = xmlDoc.querySelectorAll('url loc');

          urlElements.forEach(loc => {
            const url = loc.textContent;
            if (!pages.find(p => p.url === url)) {
              pages.push({ url: url });
            }
          });
        }
      } catch (e) {
        console.log('Sitemap not accessible:', e);
      }

      // Fetch metadata for each page
      for (const page of pages) {
        try {
          const pageData = await this.fetchPageMetadata(page.url);
          if (pageData) {
            this.aiIndex.pages.push(pageData);
          }
        } catch (e) {
          console.error('Error fetching page:', page.url, e);
        }
      }
    }

    /**
     * Fetch blog posts using Squarespace JSON API
     */
    async fetchBlogPosts() {
      if (!this.config.includeBlog) return;

      try {
        // Squarespace blog JSON endpoint
        const response = await fetch('/blog?format=json');
        if (!response.ok) return;

        const data = await response.json();

        if (data.items) {
          data.items.forEach(post => {
            this.aiIndex.pages.push({
              url: window.location.origin + post.fullUrl,
              title: post.title,
              description: post.excerpt || this.stripHtml(post.body).substring(0, 200),
              last_modified: new Date(post.modifiedOn).toISOString(),
              published_date: new Date(post.publishOn).toISOString(),
              content_type: 'blog_post',
              author: post.author?.displayName,
              keywords: post.tags || [],
              image: post.assetUrl
            });
          });
        }

        // Try to fetch more pages if paginated
        let offset = data.items?.length || 0;
        while (data.pagination?.nextPageUrl) {
          try {
            const nextResponse = await fetch(data.pagination.nextPageUrl + '&format=json');
            const nextData = await nextResponse.json();

            if (nextData.items) {
              nextData.items.forEach(post => {
                this.aiIndex.pages.push({
                  url: window.location.origin + post.fullUrl,
                  title: post.title,
                  description: post.excerpt || this.stripHtml(post.body).substring(0, 200),
                  last_modified: new Date(post.modifiedOn).toISOString(),
                  published_date: new Date(post.publishOn).toISOString(),
                  content_type: 'blog_post',
                  author: post.author?.displayName,
                  keywords: post.tags || [],
                  image: post.assetUrl
                });
              });
            }

            if (!nextData.pagination?.nextPageUrl) break;
            data.pagination = nextData.pagination;
          } catch (e) {
            break;
          }
        }
      } catch (e) {
        console.log('Blog not available:', e);
      }
    }

    /**
     * Fetch products using Squarespace Commerce API
     */
    async fetchProducts() {
      if (!this.config.includeProducts) return;

      try {
        // Squarespace products JSON endpoint
        const response = await fetch('/api/commerce/products');
        if (!response.ok) return;

        const data = await response.json();

        if (data.products) {
          data.products.forEach(product => {
            this.aiIndex.pages.push({
              url: window.location.origin + product.url,
              title: product.name,
              description: this.stripHtml(product.description || '').substring(0, 200),
              last_modified: new Date(product.modifiedOn).toISOString(),
              content_type: 'product',
              price: product.variants?.[0]?.price?.value,
              currency: product.variants?.[0]?.price?.currency,
              in_stock: product.variants?.[0]?.stock?.unlimited || product.variants?.[0]?.stock?.quantity > 0,
              image: product.images?.[0]?.url,
              keywords: product.tags || []
            });
          });
        }
      } catch (e) {
        console.log('Products not available:', e);
      }
    }

    /**
     * Fetch metadata for a specific page
     */
    async fetchPageMetadata(url) {
      try {
        const response = await fetch(url);
        if (!response.ok) return null;

        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        const title = doc.querySelector('title')?.textContent || '';
        const description = doc.querySelector('meta[name="description"]')?.content || '';
        const lastModified = doc.querySelector('meta[property="article:modified_time"]')?.content ||
                            new Date().toISOString();

        return {
          url: url,
          title: title.trim(),
          description: description.trim(),
          last_modified: lastModified,
          content_type: 'page'
        };
      } catch (e) {
        return null;
      }
    }

    /**
     * Strip HTML tags from text
     */
    stripHtml(html) {
      const tmp = document.createElement('div');
      tmp.innerHTML = html;
      return tmp.textContent || tmp.innerText || '';
    }

    /**
     * Generate the complete AI Index
     */
    async generate() {
      await this.init();
      await this.fetchPages();
      await this.fetchBlogPosts();
      await this.fetchProducts();

      // Remove duplicates by URL
      const uniquePages = [];
      const seenUrls = new Set();

      this.aiIndex.pages.forEach(page => {
        if (!seenUrls.has(page.url)) {
          seenUrls.add(page.url);
          uniquePages.push(page);
        }
      });

      this.aiIndex.pages = uniquePages;
      return this.aiIndex;
    }

    /**
     * Publish to AI Index API
     */
    async publish() {
      if (!this.config.apiKey) {
        throw new Error('API key not configured');
      }

      const response = await fetch(`${this.config.apiBaseUrl}/publish`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify(this.aiIndex)
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Failed to publish: ${error}`);
      }

      return await response.json();
    }

    /**
     * Save to localStorage for serving
     */
    save() {
      localStorage.setItem('aiindex_data', JSON.stringify(this.aiIndex));
      localStorage.setItem('aiindex_last_generated', new Date().toISOString());
    }

    /**
     * Load from localStorage
     */
    static load() {
      const data = localStorage.getItem('aiindex_data');
      return data ? JSON.parse(data) : null;
    }
  }

  /**
   * Serve AI Index JSON endpoint
   */
  function serveAIIndexEndpoint() {
    // Check if we're on the ai-index.json page
    if (window.location.pathname === '/ai-index.json') {
      const data = AIIndexGenerator.load();
      if (data) {
        document.body.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
        document.body.style.fontFamily = 'monospace';
        document.body.style.padding = '20px';
      } else {
        document.body.innerHTML = '<pre>{"error": "AI Index not generated yet"}</pre>';
      }
    }
  }

  /**
   * Auto-generate and publish on page load
   */
  async function autoGenerate() {
    // Only run on homepage or if explicitly triggered
    if (window.location.pathname !== '/' && !sessionStorage.getItem('aiindex_trigger')) {
      return;
    }

    try {
      const generator = new AIIndexGenerator(AI_INDEX_CONFIG);
      const aiIndex = await generator.generate();
      generator.save();

      // Publish if auto-publish is enabled
      if (AI_INDEX_CONFIG.autoPublish && AI_INDEX_CONFIG.apiKey) {
        await generator.publish();
        console.log('AI Index published successfully');
      }

      // Send webhook notification
      if (AI_INDEX_CONFIG.webhookUrl) {
        await fetch(AI_INDEX_CONFIG.webhookUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            event: 'ai_index_updated',
            timestamp: new Date().toISOString(),
            page_count: aiIndex.pages.length
          })
        });
      }
    } catch (error) {
      console.error('AI Index generation error:', error);
    }
  }

  /**
   * Public API
   */
  window.AIIndex = {
    generate: async function() {
      const generator = new AIIndexGenerator(AI_INDEX_CONFIG);
      const aiIndex = await generator.generate();
      generator.save();
      return aiIndex;
    },

    publish: async function() {
      const generator = new AIIndexGenerator(AI_INDEX_CONFIG);
      await generator.init();
      generator.aiIndex = AIIndexGenerator.load() || generator.aiIndex;
      return await generator.publish();
    },

    getData: function() {
      return AIIndexGenerator.load();
    },

    getConfig: function() {
      return AI_INDEX_CONFIG;
    },

    setConfig: function(config) {
      Object.keys(config).forEach(key => {
        if (key !== 'apiBaseUrl') {
          localStorage.setItem(`aiindex_${key.replace(/([A-Z])/g, '_$1').toLowerCase()}`, config[key]);
          AI_INDEX_CONFIG[key] = config[key];
        }
      });
    },

    verifyApiKey: async function(apiKey) {
      try {
        const response = await fetch(`${AI_INDEX_CONFIG.apiBaseUrl}/verify`, {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${apiKey}` }
        });
        return { valid: response.ok, status: response.status };
      } catch (error) {
        return { valid: false, error: error.message };
      }
    }
  };

  // Initialize
  document.addEventListener('DOMContentLoaded', function() {
    serveAIIndexEndpoint();

    // Auto-generate on homepage every 24 hours
    const lastGenerated = localStorage.getItem('aiindex_last_generated');
    const dayInMs = 24 * 60 * 60 * 1000;

    if (!lastGenerated || (Date.now() - new Date(lastGenerated).getTime() > dayInMs)) {
      if (AI_INDEX_CONFIG.apiKey) {
        autoGenerate();
      }
    }
  });

  console.log('AI Index for Squarespace loaded. Use window.AIIndex to interact.');
})();
