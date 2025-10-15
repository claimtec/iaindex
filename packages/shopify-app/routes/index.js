const express = require('express');
const router = express.Router();
const shopifyService = require('../services/shopify');

/**
 * Generate and publish AI Index
 */
router.post('/generate-index', async (req, res) => {
  try {
    const { shop, accessToken } = req.session;
    const aiIndex = await shopifyService.generateAIIndex(shop, accessToken);
    const result = await shopifyService.publishToTheme(shop, accessToken, aiIndex);

    res.json({
      success: true,
      message: 'AI Index generated and published successfully',
      data: result,
    });
  } catch (error) {
    console.error('Error generating index:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * Get current AI Index
 */
router.get('/ai-index', async (req, res) => {
  try {
    const { shop, accessToken } = req.session;
    const aiIndex = await shopifyService.generateAIIndex(shop, accessToken);

    res.json(aiIndex);
  } catch (error) {
    console.error('Error fetching AI Index:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * Get shop info
 */
router.get('/shop', async (req, res) => {
  try {
    const { shop } = req.session;

    res.json({
      success: true,
      shop: {
        domain: shop,
        publisher_id: shop,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

module.exports = router;
