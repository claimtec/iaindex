/**
 * Bubble.io Action: Send Access Receipt
 * Sends an access receipt to AIIndex when AI accesses content
 */

function(properties, context) {
  const documentId = properties.document_id;
  const aiProvider = properties.ai_provider;
  const accessType = properties.access_type || 'crawl';

  // Get API key from plugin settings
  const apiKey = context.keys['AIIndex API'];
  const apiEndpoint = 'https://api.aiindex.org/v1';

  if (!apiKey) {
    return {
      success: false,
      error: 'API key not configured',
      receipt_id: null,
      status: 'error'
    };
  }

  if (!documentId) {
    return {
      success: false,
      error: 'Document ID is required',
      receipt_id: null,
      status: 'error'
    };
  }

  try {
    // Prepare receipt data
    const receiptData = {
      document_id: documentId,
      ai_provider: aiProvider,
      access_type: accessType,
      timestamp: new Date().toISOString(),
      source: 'bubble.io',
      metadata: {
        user_agent: context.request?.headers?.['user-agent'],
        ip_address: context.request?.ip,
        session_id: context.session?.id
      }
    };

    // Send receipt to AIIndex API
    const response = fetch(`${apiEndpoint}/receipts`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'X-AIIndex-Plugin': 'Bubble/1.0.0'
      },
      body: JSON.stringify(receiptData)
    });

    if (response.status === 200 || response.status === 201) {
      const result = JSON.parse(response.body);

      // Store receipt in Bubble database
      saveReceiptToDatabase(result, context);

      // Trigger custom event
      context.trigger('Receipt Sent', {
        receipt_id: result.receipt_id,
        document_id: documentId,
        ai_provider: aiProvider
      });

      return {
        success: true,
        receipt_id: result.receipt_id,
        status: result.status || 'sent',
        timestamp: new Date().toISOString()
      };
    } else {
      throw new Error(`Failed to send receipt: ${response.status}`);
    }

  } catch (error) {
    return {
      success: false,
      error: error.message,
      receipt_id: null,
      status: 'error'
    };
  }
}

/**
 * Save receipt to Bubble database
 */
function saveReceiptToDatabase(receipt, context) {
  try {
    const receiptRecord = {
      type: 'AIIndex Receipt',
      receipt_id: receipt.receipt_id,
      document_id: receipt.document_id,
      ai_provider: receipt.ai_provider,
      access_type: receipt.access_type,
      timestamp: new Date(receipt.timestamp),
      status: receipt.status,
      created_date: new Date()
    };

    context.database.create(receiptRecord);
  } catch (error) {
    console.error('Failed to save receipt to database:', error);
  }
}
