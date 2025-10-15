const crypto = require('crypto');

/**
 * Generate AI Index JSON from Ghost content
 */
async function generateAIIndex(ghost) {
  const { models, urlUtils, config } = ghost;

  // Fetch site settings
  const settings = await models.Settings.findAll();
  const settingsObj = settings.reduce((obj, setting) => {
    obj[setting.get('key')] = setting.get('value');
    return obj;
  }, {});

  // Fetch published posts
  const posts = await models.Post.findAll({
    filter: 'status:published',
    limit: 'all',
    include: ['authors', 'tags']
  });

  // Fetch published pages
  const pages = await models.Post.findAll({
    filter: 'status:published+page:true',
    limit: 'all',
    include: ['authors']
  });

  // Build publisher info
  const siteUrl = urlUtils.getSiteUrl();
  const publisher = {
    id: new URL(siteUrl).hostname,
    name: settingsObj.title || 'Ghost Site',
    description: settingsObj.description || '',
    domain: new URL(siteUrl).hostname,
    type: 'blog',
    platform: 'ghost',
    logo: settingsObj.logo || null,
    icon: settingsObj.icon || null,
  };

  // Build content structure
  const content = {
    posts: posts.map(post => ({
      id: post.get('id'),
      uuid: post.get('uuid'),
      title: post.get('title'),
      slug: post.get('slug'),
      excerpt: post.get('excerpt') || post.get('custom_excerpt') || '',
      content: stripHtml(post.get('html') || '').substring(0, 500),
      url: urlUtils.urlFor('post', { post }, true),
      featured: post.get('featured'),
      feature_image: post.get('feature_image'),
      published_at: post.get('published_at'),
      updated_at: post.get('updated_at'),
      authors: post.related('authors').map(author => ({
        id: author.get('id'),
        name: author.get('name'),
        slug: author.get('slug'),
        profile_image: author.get('profile_image'),
      })),
      tags: post.related('tags').map(tag => ({
        id: tag.get('id'),
        name: tag.get('name'),
        slug: tag.get('slug'),
      })),
      primary_tag: post.related('tags').length > 0 ? {
        id: post.related('tags').at(0).get('id'),
        name: post.related('tags').at(0).get('name'),
        slug: post.related('tags').at(0).get('slug'),
      } : null,
    })),
    pages: pages.map(page => ({
      id: page.get('id'),
      uuid: page.get('uuid'),
      title: page.get('title'),
      slug: page.get('slug'),
      excerpt: page.get('excerpt') || page.get('custom_excerpt') || '',
      url: urlUtils.urlFor('page', { page }, true),
      feature_image: page.get('feature_image'),
      published_at: page.get('published_at'),
      updated_at: page.get('updated_at'),
    })),
  };

  // Build metadata
  const metadata = {
    generated_at: new Date().toISOString(),
    total_posts: content.posts.length,
    total_pages: content.pages.length,
    ghost_version: config.get('version'),
  };

  // Build access config
  const access = {
    webhook_url: `${siteUrl}/api/aiindex/access`,
    verification_required: true,
    rate_limit: {
      requests_per_hour: 100,
      burst: 10,
    },
  };

  // Assemble AI Index
  const aiIndex = {
    version: '1.0',
    publisher,
    content,
    metadata,
    access,
  };

  return aiIndex;
}

/**
 * Strip HTML tags from content
 */
function stripHtml(html) {
  return html.replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

module.exports = {
  generateAIIndex,
};
