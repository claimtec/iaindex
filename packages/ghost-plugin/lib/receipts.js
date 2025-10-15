/**
 * Record LLM access receipts
 */
async function recordAccess(accessData, ghost) {
  const { models, logging } = ghost;

  try {
    // Create a receipt record
    const receipt = {
      id: generateReceiptId(),
      llm_provider: accessData.llm_provider || 'unknown',
      content_accessed: JSON.stringify(accessData.content_accessed || []),
      timestamp: new Date(),
      metadata: JSON.stringify(accessData.metadata || {}),
      user_query: accessData.metadata?.user_query || null,
      response_included: accessData.metadata?.response_included || false,
    };

    // Store in custom table (you'll need to create this table)
    // For now, we'll log it and store in settings
    logging.info('LLM Access Receipt:', receipt);

    // Store receipts in a custom setting (for demo purposes)
    // In production, create a dedicated table
    const existingReceipts = await getStoredReceipts(ghost);
    existingReceipts.push(receipt);

    // Keep only last 1000 receipts
    const recentReceipts = existingReceipts.slice(-1000);

    await models.Settings.edit({
      key: 'aiindex_receipts',
      value: JSON.stringify(recentReceipts),
    }, { id: 'aiindex_receipts' }).catch(async () => {
      // Setting doesn't exist, create it
      await models.Settings.add({
        key: 'aiindex_receipts',
        value: JSON.stringify(recentReceipts),
        type: 'private',
      });
    });

    return receipt;
  } catch (error) {
    logging.error('Error recording access receipt:', error);
    throw error;
  }
}

/**
 * Get analytics for LLM accesses
 */
async function getAnalytics(dateRange, ghost) {
  const receipts = await getStoredReceipts(ghost);

  // Filter by date range
  const startDate = getStartDate(dateRange);
  const filteredReceipts = receipts.filter(receipt => {
    const receiptDate = new Date(receipt.timestamp);
    return receiptDate >= startDate;
  });

  // Aggregate analytics
  const analytics = {
    total_accesses: filteredReceipts.length,
    by_llm_provider: {},
    by_date: {},
    recent_accesses: filteredReceipts.slice(-50).reverse(),
  };

  filteredReceipts.forEach(receipt => {
    // By provider
    const provider = receipt.llm_provider;
    analytics.by_llm_provider[provider] = (analytics.by_llm_provider[provider] || 0) + 1;

    // By date
    const date = new Date(receipt.timestamp).toISOString().split('T')[0];
    analytics.by_date[date] = (analytics.by_date[date] || 0) + 1;
  });

  return analytics;
}

/**
 * Get stored receipts from settings
 */
async function getStoredReceipts(ghost) {
  try {
    const setting = await ghost.models.Settings.findOne({ key: 'aiindex_receipts' });
    if (setting) {
      return JSON.parse(setting.get('value'));
    }
  } catch (error) {
    // Setting doesn't exist yet
  }
  return [];
}

/**
 * Generate unique receipt ID
 */
function generateReceiptId() {
  return `receipt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Get start date for date range
 */
function getStartDate(range) {
  const now = new Date();
  switch (range) {
    case '7d':
      return new Date(now.setDate(now.getDate() - 7));
    case '30d':
      return new Date(now.setDate(now.getDate() - 30));
    case '90d':
      return new Date(now.setDate(now.getDate() - 90));
    default:
      return new Date(now.setDate(now.getDate() - 30));
  }
}

module.exports = {
  recordAccess,
  getAnalytics,
  getStoredReceipts,
};
