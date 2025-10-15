const express = require('express');
const { Shopify } = require('@shopify/shopify-api');
const path = require('path');
const shopifyService = require('./services/shopify');
const indexRoutes = require('./routes/index');
const webhookRoutes = require('./routes/webhooks');
const analyticsRoutes = require('./routes/analytics');

const app = express();
const PORT = process.env.PORT || 3000;

// Shopify configuration
Shopify.Context.initialize({
  API_KEY: process.env.SHOPIFY_API_KEY,
  API_SECRET_KEY: process.env.SHOPIFY_API_SECRET,
  SCOPES: process.env.SHOPIFY_API_SCOPES?.split(',') || ['read_themes', 'write_themes', 'read_content', 'read_analytics'],
  HOST_NAME: process.env.SHOPIFY_APP_URL.replace(/https:\/\//, ''),
  API_VERSION: '2024-01',
  IS_EMBEDDED_APP: true,
  SESSION_STORAGE: new Shopify.Session.MemorySessionStorage(),
});

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'frontend/build')));

// Raw body parser for webhooks
app.use('/api/webhooks', express.raw({ type: 'application/json' }));

// Routes
app.use('/api', indexRoutes);
app.use('/api/webhooks', webhookRoutes);
app.use('/api/analytics', analyticsRoutes);

// OAuth routes
app.get('/auth', async (req, res) => {
  const shop = req.query.shop;

  if (!shop) {
    return res.status(400).send('Missing shop parameter');
  }

  const authRoute = await Shopify.Auth.beginAuth(
    req,
    res,
    shop,
    '/auth/callback',
    false
  );

  return res.redirect(authRoute);
});

app.get('/auth/callback', async (req, res) => {
  try {
    const session = await Shopify.Auth.validateAuthCallback(
      req,
      res,
      req.query
    );

    const { shop, accessToken } = session;

    // Store session
    await Shopify.Context.SESSION_STORAGE.storeSession(session);

    // Initialize AI Index for this shop
    await shopifyService.initializeAIIndex(shop, accessToken);

    // Register webhooks
    await shopifyService.registerWebhooks(shop, accessToken);

    res.redirect(`/?shop=${shop}`);
  } catch (error) {
    console.error('Auth callback error:', error);
    res.status(500).send('Authentication failed');
  }
});

// Verify request middleware
const verifyRequest = async (req, res, next) => {
  try {
    const session = await Shopify.Utils.loadCurrentSession(req, res);

    if (!session) {
      return res.redirect(`/auth?shop=${req.query.shop}`);
    }

    req.session = session;
    next();
  } catch (error) {
    console.error('Session verification error:', error);
    res.status(401).send('Unauthorized');
  }
};

app.use('/api/*', verifyRequest);

// Serve React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend/build', 'index.html'));
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`Shopify AI Index app listening on port ${PORT}`);
});

module.exports = app;
