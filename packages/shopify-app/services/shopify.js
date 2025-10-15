const { Shopify } = require('@shopify/shopify-api');
const crypto = require('crypto');

class ShopifyService {
  /**
   * Generate AI Index JSON for a Shopify store
   */
  async generateAIIndex(shop, accessToken) {
    const client = new Shopify.Clients.Rest(shop, accessToken);

    // Fetch shop info
    const shopInfo = await client.get({
      path: 'shop',
    });

    // Fetch products
    const products = await client.get({
      path: 'products',
      query: { limit: 250, status: 'active' },
    });

    // Fetch pages
    const pages = await client.get({
      path: 'pages',
      query: { limit: 250 },
    });

    // Fetch blog posts
    const blogs = await client.get({
      path: 'blogs',
    });

    let articles = [];
    for (const blog of blogs.body.blogs) {
      const blogArticles = await client.get({
        path: `blogs/${blog.id}/articles`,
        query: { limit: 250 },
      });
      articles = articles.concat(blogArticles.body.articles);
    }

    // Build AI Index structure
    const aiIndex = {
      version: '1.0',
      publisher: {
        id: shop,
        name: shopInfo.body.shop.name,
        domain: shopInfo.body.shop.domain,
        type: 'ecommerce',
        platform: 'shopify',
      },
      content: {
        products: products.body.products.map(product => ({
          id: product.id.toString(),
          title: product.title,
          description: product.body_html?.replace(/<[^>]*>/g, '') || '',
          url: `https://${shopInfo.body.shop.domain}/products/${product.handle}`,
          price: product.variants[0]?.price || null,
          currency: shopInfo.body.shop.currency,
          images: product.images.map(img => img.src),
          tags: product.tags?.split(',').map(t => t.trim()) || [],
          published_at: product.published_at,
        })),
        pages: pages.body.pages.map(page => ({
          id: page.id.toString(),
          title: page.title,
          description: page.body_html?.replace(/<[^>]*>/g, '').substring(0, 200) || '',
          url: `https://${shopInfo.body.shop.domain}/pages/${page.handle}`,
          published_at: page.published_at,
        })),
        articles: articles.map(article => ({
          id: article.id.toString(),
          title: article.title,
          description: article.summary_html?.replace(/<[^>]*>/g, '') || article.body_html?.replace(/<[^>]*>/g, '').substring(0, 200) || '',
          url: `https://${shopInfo.body.shop.domain}/blogs/${article.blog_id}/articles/${article.handle}`,
          author: article.author,
          published_at: article.published_at,
          tags: article.tags?.split(',').map(t => t.trim()) || [],
        })),
      },
      metadata: {
        generated_at: new Date().toISOString(),
        total_products: products.body.products.length,
        total_pages: pages.body.pages.length,
        total_articles: articles.length,
      },
      access: {
        webhook_url: `${process.env.SHOPIFY_APP_URL}/api/webhooks/access`,
        verification_required: true,
      },
    };

    return aiIndex;
  }

  /**
   * Publish AI Index to theme
   */
  async publishToTheme(shop, accessToken, aiIndexData) {
    const client = new Shopify.Clients.Rest(shop, accessToken);

    // Get active theme
    const themes = await client.get({
      path: 'themes',
      query: { role: 'main' },
    });

    const activeTheme = themes.body.themes[0];

    if (!activeTheme) {
      throw new Error('No active theme found');
    }

    // Create or update ai-index.json asset
    const asset = {
      key: 'assets/ai-index.json',
      value: JSON.stringify(aiIndexData, null, 2),
    };

    await client.put({
      path: `themes/${activeTheme.id}/assets`,
      data: { asset },
    });

    // Create a snippet to inject the JSON reference into theme.liquid
    const snippetContent = `<script type="application/json" id="ai-index-metadata">
  {{ 'ai-index.json' | asset_url }}
</script>`;

    const snippet = {
      key: 'snippets/ai-index-meta.liquid',
      value: snippetContent,
    };

    await client.put({
      path: `themes/${activeTheme.id}/assets`,
      data: { asset: snippet },
    });

    return {
      theme_id: activeTheme.id,
      theme_name: activeTheme.name,
      asset_url: `https://${shop}/assets/ai-index.json`,
    };
  }

  /**
   * Initialize AI Index for a shop
   */
  async initializeAIIndex(shop, accessToken) {
    try {
      const aiIndex = await this.generateAIIndex(shop, accessToken);
      const result = await this.publishToTheme(shop, accessToken, aiIndex);
      return result;
    } catch (error) {
      console.error('Error initializing AI Index:', error);
      throw error;
    }
  }

  /**
   * Register webhooks for content updates
   */
  async registerWebhooks(shop, accessToken) {
    const client = new Shopify.Clients.Rest(shop, accessToken);

    const webhookTopics = [
      'products/create',
      'products/update',
      'products/delete',
      'pages/create',
      'pages/update',
      'pages/delete',
    ];

    for (const topic of webhookTopics) {
      try {
        await client.post({
          path: 'webhooks',
          data: {
            webhook: {
              topic,
              address: `${process.env.SHOPIFY_APP_URL}/api/webhooks/content`,
              format: 'json',
            },
          },
        });
      } catch (error) {
        console.log(`Webhook ${topic} may already exist`);
      }
    }
  }

  /**
   * Verify webhook signature
   */
  verifyWebhook(data, hmacHeader) {
    const hash = crypto
      .createHmac('sha256', process.env.SHOPIFY_API_SECRET)
      .update(data, 'utf8')
      .digest('base64');

    return hash === hmacHeader;
  }

  /**
   * Record LLM access receipt
   */
  async recordAccess(shop, accessData) {
    // Store access receipt (implement your storage logic)
    const receipt = {
      shop,
      llm_provider: accessData.llm_provider,
      content_accessed: accessData.content_accessed,
      timestamp: new Date().toISOString(),
      metadata: accessData.metadata || {},
    };

    // TODO: Store in database
    console.log('Access receipt:', receipt);

    return receipt;
  }

  /**
   * Get analytics for a shop
   */
  async getAnalytics(shop, dateRange = '30d') {
    // TODO: Implement analytics aggregation from stored receipts
    return {
      shop,
      date_range: dateRange,
      total_accesses: 0,
      by_llm_provider: {},
      by_content_type: {},
      by_date: [],
    };
  }
}

module.exports = new ShopifyService();
