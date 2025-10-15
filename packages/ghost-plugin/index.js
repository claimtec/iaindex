const path = require('path');
const generator = require('./lib/generator');
const receipts = require('./lib/receipts');
const webhooks = require('./lib/webhooks');

module.exports = {
  // Ghost integration metadata
  name: 'ghost-ai-index',
  version: '1.0.0',

  /**
   * Initialize the plugin
   */
  async init(ghost) {
    const { logging, models, urlUtils } = ghost;

    logging.info('Initializing AI Index plugin');

    // Register middleware for /ai-index.json route
    ghost.helpers.middleware.use(async (req, res, next) => {
      if (req.path === '/ai-index.json') {
        try {
          const aiIndex = await generator.generateAIIndex(ghost);
          res.json(aiIndex);
        } catch (error) {
          logging.error('Error generating AI Index:', error);
          res.status(500).json({ error: 'Failed to generate AI Index' });
        }
      } else {
        next();
      }
    });

    // Register webhook endpoint for LLM access receipts
    ghost.helpers.middleware.use('/api/aiindex/access', async (req, res) => {
      if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
      }

      try {
        const receipt = await receipts.recordAccess(req.body, ghost);
        res.json({
          success: true,
          receipt_id: receipt.id,
        });
      } catch (error) {
        logging.error('Error recording access receipt:', error);
        res.status(500).json({ error: 'Failed to record access' });
      }
    });

    // Register webhook for content updates
    ghost.events.on('post.published', async (post) => {
      logging.info('Post published, updating AI Index');
      await webhooks.handleContentUpdate('post', post, ghost);
    });

    ghost.events.on('post.unpublished', async (post) => {
      logging.info('Post unpublished, updating AI Index');
      await webhooks.handleContentUpdate('post', post, ghost);
    });

    ghost.events.on('page.published', async (page) => {
      logging.info('Page published, updating AI Index');
      await webhooks.handleContentUpdate('page', page, ghost);
    });

    ghost.events.on('page.unpublished', async (page) => {
      logging.info('Page unpublished, updating AI Index');
      await webhooks.handleContentUpdate('page', page, ghost);
    });

    logging.info('AI Index plugin initialized successfully');
  },

  /**
   * Config for Ghost admin panel
   */
  config: {
    enabled: true,
    routes: [
      {
        path: '/ai-index.json',
        method: 'GET',
        handler: 'generateIndex'
      },
      {
        path: '/api/aiindex/access',
        method: 'POST',
        handler: 'recordAccess'
      }
    ]
  }
};
