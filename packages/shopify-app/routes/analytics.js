const express = require('express');
const router = express.Router();
const shopifyService = require('../services/shopify');

/**
 * Get analytics for the authenticated shop
 */
router.get('/', async (req, res) => {
  try {
    const { shop } = req.session;
    const dateRange = req.query.range || '30d';

    const analytics = await shopifyService.getAnalytics(shop, dateRange);

    res.json({
      success: true,
      data: analytics,
    });
  } catch (error) {
    console.error('Error fetching analytics:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * Get detailed access logs
 */
router.get('/accesses', async (req, res) => {
  try {
    const { shop } = req.session;
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 50;

    // TODO: Implement pagination and fetch from database
    const accesses = [];

    res.json({
      success: true,
      data: {
        accesses,
        page,
        limit,
        total: 0,
      },
    });
  } catch (error) {
    console.error('Error fetching access logs:', error);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

module.exports = router;
