/**
 * AIIndex Webflow Integration Snippet
 * Auto-generates /ai-index.json using Webflow CMS API
 * Version: 1.0.0
 */

(function() {
  'use strict';

  const AIIndexWebflow = {
    config: {
      apiKey: null,
      domain: null,
      webhookUrl: null,
      apiEndpoint: 'https://api.aiindex.org/v1',
      badgeEnabled: true,
      autoSync: true
    },

    /**
     * Initialize the AIIndex integration
     */
    init: function(userConfig) {
      this.config = { ...this.config, ...userConfig };

      if (!this.config.apiKey) {
        console.error('AIIndex: API key is required');
        return;
      }

      if (!this.config.domain) {
        this.config.domain = window.location.hostname;
      }

      // Auto-sync on page load if enabled
      if (this.config.autoSync) {
        this.syncToAIIndex();
      }

      // Display badge if enabled
      if (this.config.badgeEnabled) {
        this.renderBadge();
      }

      // Listen for CMS updates
      this.setupCMSListeners();
    },

    /**
     * Fetch all CMS collections and generate AI Index JSON
     */
    generateAIIndexJSON: async function() {
      try {
        const collections = await this.fetchWebflowCollections();
        const items = await this.fetchAllCollectionItems(collections);

        const aiIndexData = {
          version: '1.0',
          domain: this.config.domain,
          generated: new Date().toISOString(),
          pages: this.transformToAIIndexFormat(items),
          metadata: {
            totalPages: items.length,
            collections: collections.map(c => c.name),
            lastSync: new Date().toISOString()
          }
        };

        return aiIndexData;
      } catch (error) {
        console.error('AIIndex: Error generating JSON', error);
        throw error;
      }
    },

    /**
     * Fetch Webflow CMS collections
     */
    fetchWebflowCollections: async function() {
      // In Webflow, this would integrate with Webflow API
      // For client-side, we'll use a proxy endpoint or server-side generation
      const response = await fetch(`${this.config.apiEndpoint}/webflow/collections`, {
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch Webflow collections');
      }

      return await response.json();
    },

    /**
     * Fetch all items from collections
     */
    fetchAllCollectionItems: async function(collections) {
      const allItems = [];

      for (const collection of collections) {
        try {
          const response = await fetch(
            `${this.config.apiEndpoint}/webflow/collections/${collection.id}/items`,
            {
              headers: {
                'Authorization': `Bearer ${this.config.apiKey}`,
                'Content-Type': 'application/json'
              }
            }
          );

          if (response.ok) {
            const items = await response.json();
            allItems.push(...items);
          }
        } catch (error) {
          console.error(`AIIndex: Error fetching items for ${collection.name}`, error);
        }
      }

      return allItems;
    },

    /**
     * Transform Webflow CMS data to AIIndex format
     */
    transformToAIIndexFormat: function(items) {
      return items.map(item => ({
        url: item.url || `${window.location.origin}${item.slug}`,
        title: item.name || item.title,
        description: item.description || item.summary || '',
        content: item.content || item['post-body'] || '',
        metadata: {
          published: item['published-on'] || item.createdOn,
          updated: item['updated-on'] || item.updatedOn,
          author: item.author?.name || '',
          category: item.category?.name || '',
          tags: item.tags || []
        },
        access: {
          crawlable: !item['no-index'],
          aiTrainable: true
        }
      }));
    },

    /**
     * Sync generated JSON to AIIndex API
     */
    syncToAIIndex: async function() {
      try {
        console.log('AIIndex: Starting sync...');

        const aiIndexData = await this.generateAIIndexJSON();

        const response = await fetch(`${this.config.apiEndpoint}/documents`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            domain: this.config.domain,
            data: aiIndexData
          })
        });

        if (!response.ok) {
          throw new Error('Failed to sync with AIIndex API');
        }

        const result = await response.json();
        console.log('AIIndex: Sync successful', result);

        // Trigger webhook if configured
        if (this.config.webhookUrl) {
          this.triggerWebhook(result);
        }

        return result;
      } catch (error) {
        console.error('AIIndex: Sync failed', error);
        throw error;
      }
    },

    /**
     * Verify domain with AIIndex
     */
    verifyDomain: async function() {
      try {
        const response = await fetch(`${this.config.apiEndpoint}/domains/verify`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.config.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            domain: this.config.domain
          })
        });

        if (!response.ok) {
          throw new Error('Domain verification failed');
        }

        const result = await response.json();
        console.log('AIIndex: Domain verified', result);
        return result;
      } catch (error) {
        console.error('AIIndex: Domain verification failed', error);
        throw error;
      }
    },

    /**
     * Trigger webhook notification
     */
    triggerWebhook: async function(data) {
      try {
        await fetch(this.config.webhookUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            event: 'aiindex.sync.complete',
            timestamp: new Date().toISOString(),
            data: data
          })
        });
      } catch (error) {
        console.error('AIIndex: Webhook notification failed', error);
      }
    },

    /**
     * Setup listeners for CMS updates
     */
    setupCMSListeners: function() {
      // Listen for Webflow Designer updates (if available)
      if (window.Webflow) {
        window.Webflow.push(() => {
          console.log('AIIndex: Webflow ready, monitoring for changes');
        });
      }

      // Listen for custom events
      window.addEventListener('aiindex:sync', () => {
        this.syncToAIIndex();
      });
    },

    /**
     * Render AIIndex verification badge
     */
    renderBadge: function() {
      const badge = document.createElement('div');
      badge.id = 'aiindex-badge';
      badge.innerHTML = `
        <a href="https://aiindex.org/verify/${this.config.domain}"
           target="_blank"
           rel="noopener"
           style="display: inline-flex; align-items: center; padding: 8px 12px;
                  background: #000; color: #fff; text-decoration: none;
                  border-radius: 4px; font-size: 12px; font-family: sans-serif;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style="margin-right: 6px;">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          AI Index Verified
        </a>
      `;

      // Find badge container or append to body
      const container = document.querySelector('[data-aiindex-badge]') || document.body;
      container.appendChild(badge);
    },

    /**
     * Manual trigger for sync (can be called from Webflow interactions)
     */
    manualSync: function() {
      return this.syncToAIIndex();
    },

    /**
     * Get current sync status
     */
    getStatus: async function() {
      try {
        const response = await fetch(
          `${this.config.apiEndpoint}/documents/status?domain=${this.config.domain}`,
          {
            headers: {
              'Authorization': `Bearer ${this.config.apiKey}`
            }
          }
        );

        if (response.ok) {
          return await response.json();
        }
      } catch (error) {
        console.error('AIIndex: Failed to get status', error);
      }
      return null;
    }
  };

  // Expose to global scope
  window.AIIndexWebflow = AIIndexWebflow;

  // Auto-initialize if config is present
  if (window.aiIndexConfig) {
    AIIndexWebflow.init(window.aiIndexConfig);
  }
})();
