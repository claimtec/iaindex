const express = require('express');
const router = express.Router();
const shopifyService = require('../services/shopify');

/**
 * Handle LLM access receipts
 */
router.post('/access', async (req, res) => {
  try {
    const hmac = req.get('X-Shopify-Hmac-SHA256');
    const shop = req.get('X-Shopify-Shop-Domain');
    const rawBody = req.body;

    // Verify webhook
    if (!shopifyService.verifyWebhook(rawBody, hmac)) {
      return res.status(401).json({ error: 'Invalid webhook signature' });
    }

    const accessData = JSON.parse(rawBody.toString());

    // Record the access
    const receipt = await shopifyService.recordAccess(shop, accessData);

    res.json({
      success: true,
      receipt_id: receipt.timestamp,
      message: 'Access recorded successfully',
    });
  } catch (error) {
    console.error('Error processing access webhook:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * Handle content update webhooks
 */
router.post('/content', async (req, res) => {
  try {
    const hmac = req.get('X-Shopify-Hmac-SHA256');
    const shop = req.get('X-Shopify-Shop-Domain');
    const topic = req.get('X-Shopify-Topic');
    const rawBody = req.body;

    // Verify webhook
    if (!shopifyService.verifyWebhook(rawBody, hmac)) {
      return res.status(401).json({ error: 'Invalid webhook signature' });
    }

    console.log(`Content webhook received: ${topic} for ${shop}`);

    // TODO: Queue a job to regenerate AI Index
    // For now, we'll acknowledge the webhook
    res.status(200).json({ success: true });
  } catch (error) {
    console.error('Error processing content webhook:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

module.exports = router;
