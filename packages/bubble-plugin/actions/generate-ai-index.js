/**
 * Bubble.io Action: Generate AI Index JSON
 * Generates ai-index.json from Bubble database and syncs to AIIndex API
 */

function(properties, context) {
  const domain = properties.domain;
  const dataSource = properties.data_source;
  const autoSync = properties.auto_sync !== false;

  // Get API key from plugin settings
  const apiKey = context.keys['AIIndex API'];
  const apiEndpoint = 'https://api.aiindex.org/v1';

  if (!apiKey) {
    return {
      success: false,
      error: 'API key not configured',
      document_count: 0,
      sync_status: 'error'
    };
  }

  try {
    // Fetch data from Bubble database
    const bubbleData = getBubbleData(dataSource, context);

    // Transform to AIIndex format
    const aiIndexData = transformToAIIndexFormat(bubbleData, domain);

    // Generate JSON structure
    const aiIndexJSON = {
      version: '1.0',
      domain: domain,
      generated: new Date().toISOString(),
      pages: aiIndexData,
      metadata: {
        totalPages: aiIndexData.length,
        source: 'bubble.io',
        dataType: dataSource,
        lastSync: new Date().toISOString()
      }
    };

    // Save JSON to Bubble file storage
    const jsonUrl = saveJSONToFile(aiIndexJSON, context);

    let syncResult = null;

    // Sync to AIIndex API if enabled
    if (autoSync) {
      syncResult = syncToAIIndex(aiIndexJSON, apiKey, apiEndpoint);
    }

    return {
      success: true,
      document_count: aiIndexData.length,
      sync_status: syncResult ? syncResult.status : 'local_only',
      json_url: jsonUrl,
      last_synced: new Date().toISOString()
    };

  } catch (error) {
    return {
      success: false,
      error: error.message,
      document_count: 0,
      sync_status: 'error'
    };
  }
}

/**
 * Fetch data from Bubble database
 */
function getBubbleData(dataType, context) {
  // Access Bubble's database through the context
  // This is a simplified representation - actual implementation would use Bubble's API
  const query = {
    type: dataType,
    constraints: []
  };

  // Return all published items
  return context.database.search(query);
}

/**
 * Transform Bubble data to AIIndex format
 */
function transformToAIIndexFormat(bubbleData, domain) {
  return bubbleData.map(item => {
    // Extract common fields
    const url = item.url || `https://${domain}/${item.slug || item._id}`;
    const title = item.title || item.name || '';
    const description = item.description || item.summary || '';
    const content = item.content || item.body || '';

    // Extract metadata
    const metadata = {
      published: item.created_date || item.published_date,
      updated: item.modified_date || item.updated_date,
      author: item.author?.name || item.creator?.name || '',
      category: item.category?.name || '',
      tags: item.tags || []
    };

    // Access control
    const access = {
      crawlable: item.crawlable !== false,
      aiTrainable: item.ai_trainable !== false
    };

    return {
      url,
      title,
      description,
      content,
      metadata,
      access
    };
  });
}

/**
 * Save JSON to Bubble file storage
 */
function saveJSONToFile(data, context) {
  const filename = 'ai-index.json';
  const jsonString = JSON.stringify(data, null, 2);

  // Save to Bubble file storage
  const fileUrl = context.files.save(filename, jsonString, 'application/json');

  return fileUrl;
}

/**
 * Sync to AIIndex API
 */
function syncToAIIndex(data, apiKey, apiEndpoint) {
  const response = fetch(`${apiEndpoint}/documents`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
      'X-AIIndex-Plugin': 'Bubble/1.0.0'
    },
    body: JSON.stringify({
      domain: data.domain,
      data: data
    })
  });

  if (response.status === 200 || response.status === 201) {
    return {
      status: 'synced',
      response: response.body
    };
  } else {
    throw new Error(`Sync failed: ${response.status}`);
  }
}
