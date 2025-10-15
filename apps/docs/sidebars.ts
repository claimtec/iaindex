import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // Main documentation sidebar
  mainSidebar: [
    'intro',
    'quickstart',
    {
      type: 'category',
      label: 'Publishers',
      collapsed: false,
      items: [
        'publishers/domain-verification',
        'publishers/generating-index',
        'publishers/receiving-receipts',
      ],
    },
    {
      type: 'category',
      label: 'Clients',
      collapsed: false,
      items: [
        'clients/langchain',
        'clients/llamaindex',
      ],
    },
    {
      type: 'category',
      label: 'Compliance',
      collapsed: false,
      items: [
        'compliance/gdpr',
        'compliance/popia',
        'compliance/terms',
      ],
    },
  ],

  // Protocol specification sidebar
  protocolSidebar: [
    {
      type: 'category',
      label: 'Protocol Specification',
      collapsed: false,
      items: [
        'protocol/schema',
        'protocol/receipts',
        'protocol/signatures',
      ],
    },
  ],

  // SDKs sidebar
  sdksSidebar: [
    {
      type: 'category',
      label: 'SDK Documentation',
      collapsed: false,
      items: [
        'sdks/nodejs',
        'sdks/python',
      ],
    },
  ],

  // Plugins sidebar
  pluginsSidebar: [
    {
      type: 'category',
      label: 'Website Builder Plugins',
      collapsed: false,
      items: [
        'plugins/wordpress',
        'plugins/webflow',
        'plugins/bubble',
        'plugins/wix',
        'plugins/squarespace',
        'plugins/shopify',
        'plugins/framer',
        'plugins/ghost',
      ],
    },
  ],

  // API Reference sidebar
  apiSidebar: [
    {
      type: 'category',
      label: 'API Reference',
      collapsed: false,
      items: [
        'api/authentication',
        'api/receipts',
        'api/analytics',
        'api/attestations',
      ],
    },
  ],
};

export default sidebars;
