import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'IAIndex Documentation',
  tagline: 'Transparent AI Training Attribution Protocol',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://docs.iaindex.org',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  organizationName: 'dineshanchetty', // Usually your GitHub org/user name.
  projectName: 'iaindex', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl: 'https://github.com/dineshanchetty/iaindex/tree/main/docs/',
          routeBasePath: 'docs',
          showLastUpdateAuthor: false,
          showLastUpdateTime: false,
          versions: {
            current: {
              label: 'v1.0.0',
              path: '',
            },
          },
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          editUrl: 'https://github.com/dineshanchetty/iaindex/tree/main/docs/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
        gtag: {
          trackingID: 'G-XXXXXXXXXX', // Replace with your Google Analytics ID
          anonymizeIP: true,
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/iaindex-social-card.jpg',
    metadata: [
      {name: 'keywords', content: 'AI, attribution, training data, transparency, protocol, receipts'},
      {name: 'description', content: 'IAIndex is a transparent AI training attribution protocol that enables content creators to track and verify AI usage of their content.'},
      {property: 'og:image', content: 'https://docs.iaindex.org/img/iaindex-social-card.jpg'},
      {property: 'og:type', content: 'website'},
      {name: 'twitter:card', content: 'summary_large_image'},
    ],
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'IAIndex',
      logo: {
        alt: 'IAIndex Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'mainSidebar',
          position: 'left',
          label: 'Documentation',
        },
        {
          type: 'docSidebar',
          sidebarId: 'protocolSidebar',
          position: 'left',
          label: 'Protocol',
        },
        {
          type: 'docSidebar',
          sidebarId: 'sdksSidebar',
          position: 'left',
          label: 'SDKs',
        },
        {
          type: 'docSidebar',
          sidebarId: 'pluginsSidebar',
          position: 'left',
          label: 'Plugins',
        },
        {to: '/blog', label: 'Blog', position: 'left'},
        {
          type: 'docsVersionDropdown',
          position: 'right',
          dropdownActiveClassDisabled: true,
        },
        {
          href: 'https://github.com/dineshanchetty/iaindex',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {
              label: 'Introduction',
              to: '/docs/intro',
            },
            {
              label: 'Quick Start',
              to: '/docs/quickstart',
            },
            {
              label: 'Protocol',
              to: '/docs/protocol/schema',
            },
            {
              label: 'API Reference',
              to: '/docs/api/authentication',
            },
          ],
        },
        {
          title: 'Developers',
          items: [
            {
              label: 'SDKs',
              to: '/docs/sdks/nodejs',
            },
            {
              label: 'Plugins',
              to: '/docs/plugins/wordpress',
            },
            {
              label: 'Publishers',
              to: '/docs/publishers/domain-verification',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/dineshanchetty/iaindex',
            },
            {
              label: 'Discord',
              href: 'https://discord.gg/iaindex',
            },
            {
              label: 'Twitter',
              href: 'https://twitter.com/iaindex',
            },
          ],
        },
        {
          title: 'Legal',
          items: [
            {
              label: 'Terms of Service',
              to: '/docs/compliance/terms',
            },
            {
              label: 'GDPR Compliance',
              to: '/docs/compliance/gdpr',
            },
            {
              label: 'POPIA Compliance',
              to: '/docs/compliance/popia',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Claimtec. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'json', 'python', 'javascript', 'typescript', 'php', 'ruby'],
    },
    algolia: {
      // The application ID provided by Algolia
      appId: 'YOUR_APP_ID',
      // Public API key: it is safe to commit it
      apiKey: 'YOUR_SEARCH_API_KEY',
      indexName: 'iaindex',
      // Optional: see doc section below
      contextualSearch: true,
      // Optional: Algolia search parameters
      searchParameters: {},
      // Optional: path for search page that enabled by default (`false` to disable it)
      searchPagePath: 'search',
    },
    announcementBar: {
      id: 'support_us',
      content:
        '⭐️ If you like IAIndex, give it a star on <a target="_blank" rel="noopener noreferrer" href="https://github.com/dineshanchetty/iaindex">GitHub</a>',
      backgroundColor: '#fafbfc',
      textColor: '#091E42',
      isCloseable: true,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
