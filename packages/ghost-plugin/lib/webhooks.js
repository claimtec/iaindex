const generator = require('./generator');

/**
 * Handle content update events
 */
async function handleContentUpdate(type, content, ghost) {
  const { logging } = ghost;

  try {
    logging.info(`Content update: ${type} - ${content.get('title')}`);

    // Regenerate AI Index (could be cached or queued)
    // For now, we'll just log it
    // In production, you might want to:
    // 1. Queue a job to regenerate the index
    // 2. Cache the index with a TTL
    // 3. Invalidate cache on content updates

    // Optionally, notify external services
    const webhookUrl = process.env.AIINDEX_WEBHOOK_URL;
    if (webhookUrl) {
      await notifyWebhook(webhookUrl, {
        event: 'content_updated',
        type,
        content_id: content.get('id'),
        content_title: content.get('title'),
        timestamp: new Date().toISOString(),
      });
    }
  } catch (error) {
    logging.error('Error handling content update:', error);
  }
}

/**
 * Notify external webhook
 */
async function notifyWebhook(url, data) {
  try {
    const fetch = (await import('node-fetch')).default;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      console.error('Webhook notification failed:', response.statusText);
    }
  } catch (error) {
    console.error('Error notifying webhook:', error);
  }
}

module.exports = {
  handleContentUpdate,
  notifyWebhook,
};
