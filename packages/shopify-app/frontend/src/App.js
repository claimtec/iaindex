import React, { useState, useEffect, useCallback } from 'react';
import {
  AppProvider,
  Page,
  Card,
  Layout,
  Button,
  Banner,
  TextContainer,
  Heading,
  Stack,
  Badge,
  DataTable,
  EmptyState,
  Spinner,
} from '@shopify/polaris';
import { Provider as AppBridgeProvider } from '@shopify/app-bridge-react';
import '@shopify/polaris/build/esm/styles.css';
import Dashboard from './components/Dashboard';
import AIIndexViewer from './components/AIIndexViewer';
import PolicySettings from './components/PolicySettings';
import VerificationBadge from './components/VerificationBadge';

function App() {
  const [shop, setShop] = useState(null);
  const [aiIndex, setAIIndex] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');

  const appBridgeConfig = {
    apiKey: process.env.REACT_APP_SHOPIFY_API_KEY,
    host: new URLSearchParams(window.location.search).get('host'),
    forceRedirect: true,
  };

  useEffect(() => {
    fetchShopInfo();
    fetchAIIndex();
  }, []);

  const fetchShopInfo = async () => {
    try {
      const response = await fetch('/api/shop');
      const data = await response.json();
      if (data.success) {
        setShop(data.shop);
      }
    } catch (err) {
      console.error('Error fetching shop info:', err);
    }
  };

  const fetchAIIndex = async () => {
    try {
      const response = await fetch('/api/ai-index');
      const data = await response.json();
      setAIIndex(data);
    } catch (err) {
      console.error('Error fetching AI Index:', err);
    }
  };

  const handleGenerateIndex = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/generate-index', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (data.success) {
        setSuccess('AI Index generated and published successfully!');
        await fetchAIIndex();
      } else {
        setError(data.error || 'Failed to generate AI Index');
      }
    } catch (err) {
      setError('An error occurred while generating the AI Index');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppBridgeProvider config={appBridgeConfig}>
      <AppProvider i18n={{}}>
        <Page
          title="AI Index for Shopify"
          subtitle="Make your store discoverable by AI assistants"
        >
          <Layout>
            {error && (
              <Layout.Section>
                <Banner status="critical" onDismiss={() => setError(null)}>
                  <p>{error}</p>
                </Banner>
              </Layout.Section>
            )}

            {success && (
              <Layout.Section>
                <Banner status="success" onDismiss={() => setSuccess(null)}>
                  <p>{success}</p>
                </Banner>
              </Layout.Section>
            )}

            <Layout.Section>
              <Card>
                <Card.Section>
                  <Stack distribution="equalSpacing" alignment="center">
                    <Stack vertical spacing="tight">
                      <Heading>Publisher ID</Heading>
                      <TextContainer>
                        <p>
                          <Badge status="info">{shop?.domain || 'Loading...'}</Badge>
                        </p>
                      </TextContainer>
                    </Stack>
                    <Button
                      primary
                      loading={loading}
                      onClick={handleGenerateIndex}
                    >
                      Generate AI Index
                    </Button>
                  </Stack>
                </Card.Section>
              </Card>
            </Layout.Section>

            <Layout.Section>
              <Card>
                <Card.Section>
                  <Stack distribution="equalSpacing">
                    <Button
                      plain={activeTab !== 'dashboard'}
                      pressed={activeTab === 'dashboard'}
                      onClick={() => setActiveTab('dashboard')}
                    >
                      Dashboard
                    </Button>
                    <Button
                      plain={activeTab !== 'policies'}
                      pressed={activeTab === 'policies'}
                      onClick={() => setActiveTab('policies')}
                    >
                      Policy Controls
                    </Button>
                    <Button
                      plain={activeTab !== 'verification'}
                      pressed={activeTab === 'verification'}
                      onClick={() => setActiveTab('verification')}
                    >
                      Verification
                    </Button>
                    <Button
                      plain={activeTab !== 'index'}
                      pressed={activeTab === 'index'}
                      onClick={() => setActiveTab('index')}
                    >
                      AI Index
                    </Button>
                  </Stack>
                </Card.Section>

                <Card.Section>
                  {activeTab === 'dashboard' && <Dashboard />}
                  {activeTab === 'policies' && <PolicySettings />}
                  {activeTab === 'verification' && <VerificationBadge />}
                  {activeTab === 'index' && <AIIndexViewer aiIndex={aiIndex} />}
                </Card.Section>
              </Card>
            </Layout.Section>
          </Layout>
        </Page>
      </AppProvider>
    </AppBridgeProvider>
  );
}

export default App;
