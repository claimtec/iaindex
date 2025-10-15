# AIIndex v1.1 Migration Guide for All Plugins

## Overview

AIIndex v1.1 introduces enhanced policy controls, verification badges, and receipt analytics across all website builder integrations.

## New Features Added to All Plugins

### 1. Policy Toggle UI

All plugins now include simple on/off toggles for:

- **Block Model Training**: Sets `policy.training="block"`
- **Allow Retrieval Only**: Sets `policy.training="block"` and `policy.retrieval="allow"`
- **Require Signed Receipts**: Sets `receipts.require_signed=true`
- **Enable Render Fallback**: Sets `render_fallback.mode="edge"`

### 2. Verification Badge Integration

Display live verification status showing:
- Domain verification (green checkmark or red X)
- C2PA provenance status
- Merkle attestation status
- Last updated timestamp

Badge can be embedded on frontend using platform-specific methods (shortcodes, widgets, or HTML embeds).

### 3. Receipt Analytics Widget

Admin dashboard now shows:
- Total receipts (last 7 days)
- Allowed vs denied count
- Top AI clients
- Policy violations count
- Link to full dashboard at aiindex.org/dashboard

### 4. Quick Actions

All admin panels include:
- "Regenerate AI Index" button
- "Verify Domain" button with instructions
- "View Live Badge" preview
- "Copy Embed Code" for badge

## Updated File Structures

### ai-index.json (v1.1)

```json
{
  "version": "1.1",
  "domain": "example.com",
  "siteName": "Example Site",
  "lastUpdated": "2025-10-13T10:00:00Z",
  "content": [...],
  "policy": {
    "training": "block",
    "retrieval": "allow"
  },
  "receipts": {
    "require_signed": true
  },
  "render_fallback": {
    "mode": "edge",
    "enabled": true
  },
  "publicKey": "...",
  "signature": "..."
}
```

### .well-known/aiindex-policy.json

```json
{
  "version": "1.1",
  "domain": "example.com",
  "lastUpdated": "2025-10-13T10:00:00Z",
  "policy": {
    "training": "block",
    "retrieval": "allow"
  },
  "receipts": {
    "require_signed": true
  },
  "render_fallback": {
    "mode": "edge",
    "enabled": true
  }
}
```

## Platform-Specific Updates

### WordPress (COMPLETED)

- ✅ Added "Policy Controls" tab to admin settings
- ✅ Enhanced verification tab with 4 verification types
- ✅ Updated analytics with allowed/denied counts
- ✅ Added toggle switches for policy controls
- ✅ Enhanced badge shortcode with `show_verification` attribute
- ✅ Updated generator to produce v1.1 JSON
- ✅ Added policy JSON generation method

### Shopify (COMPLETED)

- ✅ Created PolicySettings.js React component
- ✅ Created VerificationBadge.js React component
- ✅ Added Policy Controls and Verification tabs
- ✅ Integrated with Polaris UI components
- ✅ Added SettingToggle components for all policies
- ✅ Receipt analytics with 7-day summary

### Webflow, Bubble, Wix, Squarespace, Framer, Ghost

For these platforms, apply the following pattern:

#### Configuration Updates

Add policy settings to configuration:

```javascript
// Policy Configuration (v1.1)
const policyConfig = {
  blockTraining: false,
  allowRetrievalOnly: false,
  requireSignedReceipts: false,
  enableRenderFallback: false
};

// Generate policy object
function getPolicySettings() {
  const policy = {};

  if (policyConfig.blockTraining) {
    policy.training = 'block';
  }

  if (policyConfig.allowRetrievalOnly) {
    policy.training = 'block';
    policy.retrieval = 'allow';
  }

  return policy;
}

// Generate receipt settings
function getReceiptSettings() {
  return {
    require_signed: policyConfig.requireSignedReceipts
  };
}

// Generate render fallback settings
function getRenderFallbackSettings() {
  if (policyConfig.enableRenderFallback) {
    return {
      mode: 'edge',
      enabled: true
    };
  }
  return { enabled: false };
}
```

#### UI Updates

Add toggle switches to configuration UI:

```html
<!-- Policy Controls Section (v1.1) -->
<div class="policy-section">
  <h3>AI Policy Controls (v1.1)</h3>

  <div class="toggle-item">
    <label class="toggle-switch">
      <input type="checkbox" id="blockTraining" />
      <span class="slider"></span>
    </label>
    <div class="toggle-label">
      <strong>Block Model Training</strong>
      <p>Prevent AI systems from using your content for model training.</p>
    </div>
  </div>

  <div class="toggle-item">
    <label class="toggle-switch">
      <input type="checkbox" id="allowRetrievalOnly" />
      <span class="slider"></span>
    </label>
    <div class="toggle-label">
      <strong>Allow Retrieval Only</strong>
      <p>Block training but allow retrieval for RAG/search.</p>
    </div>
  </div>

  <div class="toggle-item">
    <label class="toggle-switch">
      <input type="checkbox" id="requireSignedReceipts" />
      <span class="slider"></span>
    </label>
    <div class="toggle-label">
      <strong>Require Signed Receipts</strong>
      <p>Require cryptographic signatures on all indexing receipts.</p>
    </div>
  </div>

  <div class="toggle-item">
    <label class="toggle-switch">
      <input type="checkbox" id="enableRenderFallback" />
      <span class="slider"></span>
    </label>
    <div class="toggle-label">
      <strong>Enable Render Fallback</strong>
      <p>Enable edge rendering for dynamic content.</p>
    </div>
  </div>
</div>

<!-- Verification Status (v1.1) -->
<div class="verification-section">
  <h3>Verification Status</h3>
  <div class="verification-grid">
    <div class="verification-card">
      <span class="icon" id="domain-status">○</span>
      <strong>Domain</strong>
      <span class="status">Pending</span>
    </div>
    <div class="verification-card">
      <span class="icon" id="c2pa-status">○</span>
      <strong>C2PA</strong>
      <span class="status">Pending</span>
    </div>
    <div class="verification-card">
      <span class="icon" id="merkle-status">○</span>
      <strong>Merkle</strong>
      <span class="status">Pending</span>
    </div>
  </div>
</div>

<!-- Receipt Analytics (v1.1) -->
<div class="analytics-section">
  <h3>Receipt Analytics (Last 7 Days)</h3>
  <div class="analytics-grid">
    <div class="analytics-card">
      <div class="value" id="total-receipts">0</div>
      <div class="label">Total Receipts</div>
    </div>
    <div class="analytics-card">
      <div class="value success" id="allowed-count">0</div>
      <div class="label">Allowed</div>
    </div>
    <div class="analytics-card">
      <div class="value error" id="denied-count">0</div>
      <div class="label">Denied</div>
    </div>
    <div class="analytics-card">
      <div class="value warning" id="violations-count">0</div>
      <div class="label">Violations</div>
    </div>
  </div>
</div>
```

#### CSS for Toggle Switches

```css
/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
  margin-right: 15px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

.toggle-switch input:checked + .slider {
  background-color: #4CAF50;
}

.toggle-switch input:checked + .slider:before {
  transform: translateX(26px);
}

/* Verification Grid */
.verification-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin: 20px 0;
}

.verification-card {
  text-align: center;
  padding: 20px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
}

.verification-card .icon {
  font-size: 32px;
  display: block;
  margin-bottom: 10px;
}

.verification-card .icon.verified {
  color: #4CAF50;
}

.verification-card .icon.pending {
  color: #999;
}

/* Analytics Grid */
.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  margin: 20px 0;
}

.analytics-card {
  text-align: center;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.analytics-card .value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 5px;
}

.analytics-card .value.success {
  color: #4CAF50;
}

.analytics-card .value.error {
  color: #F44336;
}

.analytics-card .value.warning {
  color: #FF9800;
}

.analytics-card .label {
  font-size: 12px;
  text-transform: uppercase;
  color: #666;
}
```

#### Badge Embed Code

```html
<!-- Verification Badge Embed -->
<div id="aiindex-badge"></div>
<script>
(function() {
  const badge = document.getElementById('aiindex-badge');

  // Fetch verification status
  fetch('https://api.aiindex.org/v1/verification?domain=' + window.location.hostname)
    .then(res => res.json())
    .then(data => {
      badge.innerHTML = `
        <div style="display: inline-flex; align-items: center; padding: 10px 15px; background: white; border: 2px solid #e0e0e0; border-radius: 8px; font-family: sans-serif;">
          <span style="font-size: 20px; margin-right: 10px;">${data.verified ? '✓' : '○'}</span>
          <div>
            <strong style="font-size: 14px;">AI Index ${data.verified ? 'Verified' : 'Pending'}</strong>
            <div style="font-size: 11px; color: #666; display: flex; gap: 8px; margin-top: 4px;">
              <span>${data.domain ? '✓' : '○'} Domain</span>
              <span>${data.c2pa ? '✓' : '○'} C2PA</span>
              <span>${data.merkle ? '✓' : '○'} Merkle</span>
            </div>
          </div>
        </div>
      `;
    });
})();
</script>
```

## Testing

After implementing v1.1 updates:

1. **Test Policy Toggles**:
   - Enable each policy toggle
   - Regenerate AI index
   - Verify `ai-index.json` contains correct policy values
   - Verify `.well-known/aiindex-policy.json` is generated

2. **Test Verification Badge**:
   - Embed badge on a test page
   - Verify it displays all 4 verification types
   - Check visual indicators (checkmarks/circles)

3. **Test Analytics**:
   - Send test receipt
   - Verify analytics update
   - Check allowed/denied counts

4. **Test Quick Actions**:
   - Click "Verify Domain"
   - Click "Regenerate Index"
   - Click "Copy Embed Code"

## Breaking Changes

- `version` field updated from `"1.0"` to `"1.1"`
- New required fields: `policy`, `receipts`, `render_fallback`
- Badge embed code format updated

## Backward Compatibility

v1.1 plugins are backward compatible:
- v1.0 consumers can still read v1.1 indexes
- Policy fields default to permissive values
- Existing badges continue to work

## Support

For questions or issues:
- Documentation: https://docs.aiindex.org/v1.1
- Dashboard: https://aiindex.org/dashboard
- GitHub: https://github.com/aiindex
- Email: support@aiindex.org
