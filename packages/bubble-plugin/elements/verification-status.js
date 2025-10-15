/**
 * Bubble.io Element: Verification Status
 * Displays domain verification status
 */

function(instance, properties) {
  const domain = properties.domain || window.location.hostname;
  const showIcon = properties.show_icon !== false;
  const compactMode = properties.compact_mode || false;

  // Get API key from plugin settings
  const apiKey = instance.data.api_key;
  const apiEndpoint = 'https://api.aiindex.org/v1';

  // Initial loading state
  renderLoadingState(instance, compactMode);

  // Fetch verification status
  fetchVerificationStatus(domain, apiKey, apiEndpoint)
    .then(status => {
      renderStatus(instance, status, showIcon, compactMode);
      instance.publishState('verification_status', status.status);
      instance.publishState('is_verified', status.status === 'verified');
    })
    .catch(error => {
      renderErrorState(instance, error.message, compactMode);
      instance.publishState('verification_status', 'error');
      instance.publishState('is_verified', false);
    });
}

/**
 * Render loading state
 */
function renderLoadingState(instance, compact) {
  const html = compact ? `
    <div style="
      display: inline-flex;
      align-items: center;
      padding: 4px 8px;
      background: #f3f4f6;
      border-radius: 4px;
      font-size: 12px;
      color: #6b7280;
    ">
      <span class="spinner" style="
        width: 12px;
        height: 12px;
        border: 2px solid #e5e7eb;
        border-top-color: #6b7280;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        margin-right: 6px;
      "></span>
      Checking...
    </div>
  ` : `
    <div style="
      display: flex;
      align-items: center;
      padding: 12px 16px;
      background: #f3f4f6;
      border-radius: 8px;
      font-size: 14px;
      color: #6b7280;
    ">
      <span class="spinner" style="
        width: 16px;
        height: 16px;
        border: 2px solid #e5e7eb;
        border-top-color: #6b7280;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        margin-right: 10px;
      "></span>
      Checking verification status...
    </div>
  `;

  instance.canvas.html(`
    <style>
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    </style>
    ${html}
  `);
}

/**
 * Render verification status
 */
function renderStatus(instance, status, showIcon, compact) {
  const statusConfig = {
    verified: {
      icon: '✓',
      label: 'Verified',
      color: '#10b981',
      background: '#d1fae5',
      borderColor: '#6ee7b7'
    },
    pending: {
      icon: '⏱',
      label: 'Pending Verification',
      color: '#f59e0b',
      background: '#fef3c7',
      borderColor: '#fcd34d'
    },
    failed: {
      icon: '✕',
      label: 'Verification Failed',
      color: '#ef4444',
      background: '#fee2e2',
      borderColor: '#fca5a5'
    },
    unverified: {
      icon: '!',
      label: 'Not Verified',
      color: '#6b7280',
      background: '#f3f4f6',
      borderColor: '#d1d5db'
    }
  };

  const config = statusConfig[status.status] || statusConfig.unverified;

  const iconHTML = showIcon ? `
    <span style="
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: ${compact ? '16px' : '20px'};
      height: ${compact ? '16px' : '20px'};
      background: ${config.color};
      color: white;
      border-radius: 50%;
      font-size: ${compact ? '10px' : '12px'};
      font-weight: bold;
      margin-right: ${compact ? '6px' : '10px'};
    ">
      ${config.icon}
    </span>
  ` : '';

  const detailsHTML = !compact && status.verified_at ? `
    <div style="
      font-size: 12px;
      color: #6b7280;
      margin-top: 4px;
    ">
      Verified on ${new Date(status.verified_at).toLocaleDateString()}
    </div>
  ` : '';

  const html = `
    <div style="
      display: ${compact ? 'inline-flex' : 'flex'};
      align-items: center;
      padding: ${compact ? '6px 10px' : '12px 16px'};
      background: ${config.background};
      border: 1px solid ${config.borderColor};
      border-radius: ${compact ? '4px' : '8px'};
      font-size: ${compact ? '12px' : '14px'};
      color: ${config.color};
      font-weight: 600;
    ">
      ${iconHTML}
      <div style="flex: 1;">
        <div>${config.label}</div>
        ${detailsHTML}
      </div>
    </div>
  `;

  instance.canvas.html(html);
}

/**
 * Render error state
 */
function renderErrorState(instance, errorMessage, compact) {
  const html = compact ? `
    <div style="
      display: inline-flex;
      align-items: center;
      padding: 6px 10px;
      background: #fee2e2;
      border: 1px solid #fca5a5;
      border-radius: 4px;
      font-size: 12px;
      color: #ef4444;
    ">
      ✕ Error
    </div>
  ` : `
    <div style="
      padding: 12px 16px;
      background: #fee2e2;
      border: 1px solid #fca5a5;
      border-radius: 8px;
      font-size: 14px;
      color: #ef4444;
    ">
      <div style="font-weight: 600; margin-bottom: 4px;">
        Verification Check Failed
      </div>
      <div style="font-size: 12px; color: #991b1b;">
        ${errorMessage}
      </div>
    </div>
  `;

  instance.canvas.html(html);
}

/**
 * Fetch verification status from API
 */
async function fetchVerificationStatus(domain, apiKey, apiEndpoint) {
  if (!apiKey) {
    throw new Error('API key not configured');
  }

  try {
    const response = await fetch(`${apiEndpoint}/domains/${domain}/status`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'X-AIIndex-Plugin': 'Bubble/1.0.0'
      }
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    throw new Error(`Failed to fetch verification status: ${error.message}`);
  }
}

// Element update function
function update(instance, properties) {
  render(instance, properties);
}

// Element reset function
function reset(instance) {
  instance.canvas.empty();
  instance.publishState('verification_status', null);
  instance.publishState('is_verified', false);
}

// Export element functions
return {
  initialize: function(instance, properties) {
    render(instance, properties);
  },
  update: update,
  reset: reset
};
