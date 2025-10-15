import React, { useState, useEffect } from 'react';
import {
  Card,
  Stack,
  TextContainer,
  Heading,
  DisplayText,
  DataTable,
  EmptyState,
  Spinner,
  Select,
} from '@shopify/polaris';

function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('30d');

  useEffect(() => {
    fetchAnalytics();
  }, [dateRange]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/analytics?range=${dateRange}`);
      const data = await response.json();
      if (data.success) {
        setAnalytics(data.data);
      }
    } catch (err) {
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <Spinner size="large" />
      </div>
    );
  }

  if (!analytics) {
    return (
      <EmptyState
        heading="No analytics data available"
        image="https://cdn.shopify.com/s/files/1/0262/4071/2726/files/emptystate-files.png"
      >
        <p>Analytics will appear here once AI assistants access your content.</p>
      </EmptyState>
    );
  }

  const llmProviderData = Object.entries(analytics.by_llm_provider || {}).map(
    ([provider, count]) => [provider, count]
  );

  const contentTypeData = Object.entries(analytics.by_content_type || {}).map(
    ([type, count]) => [type, count]
  );

  return (
    <Stack vertical>
      <Stack distribution="trailing">
        <Select
          label="Date Range"
          options={[
            { label: 'Last 7 days', value: '7d' },
            { label: 'Last 30 days', value: '30d' },
            { label: 'Last 90 days', value: '90d' },
          ]}
          value={dateRange}
          onChange={setDateRange}
        />
      </Stack>

      <Card sectioned>
        <Stack distribution="fillEvenly">
          <Stack vertical spacing="tight">
            <Heading>Total AI Accesses</Heading>
            <DisplayText size="large">{analytics.total_accesses}</DisplayText>
          </Stack>
        </Stack>
      </Card>

      {llmProviderData.length > 0 && (
        <Card sectioned title="AI Accesses by Provider">
          <DataTable
            columnContentTypes={['text', 'numeric']}
            headings={['Provider', 'Accesses']}
            rows={llmProviderData}
          />
        </Card>
      )}

      {contentTypeData.length > 0 && (
        <Card sectioned title="Accesses by Content Type">
          <DataTable
            columnContentTypes={['text', 'numeric']}
            headings={['Content Type', 'Accesses']}
            rows={contentTypeData}
          />
        </Card>
      )}
    </Stack>
  );
}

export default Dashboard;
