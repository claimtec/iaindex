// Docusaurus configuration file with AIIndex plugin integration
// https://docusaurus.io/docs/api/docusaurus-config

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'CloudForge Documentation',
  tagline: 'Open-source cloud infrastructure platform',
  favicon: 'img/favicon.ico',

  url: 'https://cloudforge-docs.dev',
  baseUrl: '/',

  organizationName: 'cloudforge',
  projectName: 'cloudforge-docs',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/cloudforge/cloudforge-docs/edit/main/',
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  plugins: [
    // AIIndex Plugin Configuration
    [
      '@aiindex/docusaurus-plugin',
      {
        // Required: Publisher identification
        publisherId: 'cloudforge-docs.dev',
        domain: 'cloudforge-docs.dev',

        // Publisher information
        publisherInfo: {
          name: 'CloudForge Documentation',
          description: 'Comprehensive documentation for CloudForge, an open-source cloud infrastructure platform',
          url: 'https://cloudforge-docs.dev',
          contact: {
            email: 'docs@cloudforge.dev',
            url: 'https://cloudforge-docs.dev/contact'
          },
          logo: 'https://cloudforge-docs.dev/img/logo.svg'
        },

        // Access control policy
        accessPolicy: {
          allowed: true,
          attributionRequired: true,
          commercialUse: true,
          receiptRequired: true,
          webhookUrl: 'https://cloudforge-docs.dev/api/aiindex/receipts'
        },

        // Content filtering
        includePaths: [
          '/docs/**',           // Include all documentation
          '/api/**',            // Include API docs
          '/guides/**'          // Include guides
        ],
        excludePaths: [
          '/blog/**',           // Exclude blog
          '/internal/**',       // Exclude internal docs
          '/drafts/**'          // Exclude drafts
        ],

        // Auto-generate summaries from doc content
        generateSummaries: true,
        summaryOptions: {
          maxLength: 2000,              // Max summary length
          includeCodeExamples: false,   // Don't include code in summaries
          focusOnCommands: true,        // Emphasize CLI commands
          stripHtml: true,              // Remove HTML tags
          language: 'en'                // Summary language
        },

        // Entity extraction (automatically find products, orgs, etc.)
        extractEntities: true,
        entityOptions: {
          extractProducts: true,
          extractOrganizations: true,
          extractPeople: false,         // Don't extract individual contributors
          customExtractors: []
        },

        // FAQ extraction from docs
        extractFAQ: true,
        faqOptions: {
          fromHeaders: true,            // Extract from Q&A style headers
          fromFrontmatter: true,        // Extract from frontmatter
          minQuestions: 3               // Minimum questions to include
        },

        // Build-time generation
        generateOnBuild: true,
        generateOnWatch: true,          // Also generate in dev mode
        outputPath: 'static/.well-known/ai-index.json',

        // Versioning support
        versioning: {
          enabled: true,
          includeAllVersions: false,    // Only include current version
          versionPath: 'docs',
          currentVersion: '2.5.0'
        },

        // API documentation integration
        apiDocs: {
          enabled: true,
          openApiUrl: 'https://api.cloudforge-docs.dev/openapi.json',
          includeInIndex: true,
          format: 'openapi3'
        },

        // Additional metadata
        metadata: {
          platform: 'Docusaurus',
          docusaurus_version: '3.0.0',
          plugin_version: 'aiindex-docusaurus-1.0.0',
          language: 'en',
          content_license: 'CC BY 4.0',
          code_license: 'Apache 2.0',
          version: '2.5.0',
          update_frequency: 'weekly',
          search_enabled: true
        },

        // Verification (will be populated after verification process)
        verification: {
          verified: true,
          verified_at: '2025-10-03T00:00:00Z',
          verification_url: 'https://aiindex.org/publishers/cloudforge-docs.dev'
        },

        // Advanced options
        advanced: {
          cacheResults: true,           // Cache generated data
          cacheDuration: 3600,          // Cache for 1 hour
          parallelProcessing: true,     // Process docs in parallel
          maxWorkers: 4,                // Max parallel workers
          verbose: false,               // Verbose logging
          debugMode: false              // Debug mode
        }
      }
    ]
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Navbar configuration
      navbar: {
        title: 'CloudForge',
        logo: {
          alt: 'CloudForge Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'doc',
            docId: 'getting-started',
            position: 'left',
            label: 'Docs',
          },
          {
            type: 'doc',
            docId: 'api-reference',
            position: 'left',
            label: 'API',
          },
          {
            href: 'https://github.com/cloudforge/cloudforge',
            label: 'GitHub',
            position: 'right',
          },
          // AIIndex verification badge
          {
            type: 'html',
            position: 'right',
            value: '<a href="https://aiindex.org/publishers/cloudforge-docs.dev" target="_blank" rel="noopener" class="navbar__aiindex" title="AIIndex Verified Publisher">AIIndex Verified</a>'
          }
        ],
      },

      // Footer configuration
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Getting Started',
                to: '/docs/getting-started',
              },
              {
                label: 'API Reference',
                to: '/docs/api-reference',
              },
              {
                label: 'CLI Reference',
                to: '/docs/cli-reference',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/cloudforge/cloudforge',
              },
              {
                label: 'Discord',
                href: 'https://discord.gg/cloudforge',
              },
              {
                label: 'Twitter',
                href: 'https://twitter.com/cloudforge',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Blog',
                href: 'https://cloudforge.dev/blog',
              },
              {
                label: 'Status',
                href: 'https://status.cloudforge.dev',
              },
            ],
          },
          {
            title: 'AI Access',
            items: [
              {
                label: 'AIIndex Verified',
                href: 'https://aiindex.org/publishers/cloudforge-docs.dev',
              },
              {
                label: 'AI-Index JSON',
                href: '/.well-known/ai-index.json',
              },
              {
                label: 'Access Policy',
                to: '/docs/ai-access-policy',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} CloudForge Foundation. Built with Docusaurus. <br/><a href="https://aiindex.org/publishers/cloudforge-docs.dev" target="_blank" rel="noopener" style="display:inline-block;margin-top:10px;"><img src="https://aiindex.org/badge.svg" alt="AIIndex Verified" width="120" height="40" loading="lazy" /></a>`,
      },

      // Prism theme for code blocks
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['bash', 'yaml', 'json', 'docker', 'go'],
      },

      // Algolia search (optional)
      algolia: {
        appId: 'YOUR_APP_ID',
        apiKey: 'YOUR_SEARCH_API_KEY',
        indexName: 'cloudforge-docs',
        contextualSearch: true,
      },

      // Announcement bar
      announcementBar: {
        id: 'aiindex_verified',
        content:
          '⚡ This documentation is AI-accessible via <a target="_blank" rel="noopener noreferrer" href="https://aiindex.org">AIIndex</a>. <a href="/.well-known/ai-index.json">View AI-Index</a>',
        backgroundColor: '#4F46E5',
        textColor: '#ffffff',
        isCloseable: true,
      },

      // Color mode
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
    }),
};

module.exports = config;
