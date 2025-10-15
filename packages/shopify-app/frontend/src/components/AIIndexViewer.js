import React from 'react';
import {
  Card,
  Stack,
  TextContainer,
  Heading,
  Badge,
  EmptyState,
  Spinner,
} from '@shopify/polaris';

function AIIndexViewer({ aiIndex }) {
  if (!aiIndex) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <Spinner size="large" />
      </div>
    );
  }

  return (
    <Stack vertical>
      <Card sectioned>
        <Stack vertical spacing="tight">
          <Heading>Publisher Information</Heading>
          <TextContainer>
            <p><strong>Name:</strong> {aiIndex.publisher.name}</p>
            <p><strong>Domain:</strong> {aiIndex.publisher.domain}</p>
            <p><strong>Publisher ID:</strong> {aiIndex.publisher.id}</p>
            <p><strong>Type:</strong> <Badge>{aiIndex.publisher.type}</Badge></p>
            <p><strong>Platform:</strong> <Badge status="info">{aiIndex.publisher.platform}</Badge></p>
          </TextContainer>
        </Stack>
      </Card>

      <Card sectioned>
        <Stack vertical spacing="tight">
          <Heading>Content Summary</Heading>
          <Stack distribution="fillEvenly">
            <Stack vertical spacing="extraTight">
              <TextContainer>
                <p><strong>Products</strong></p>
                <Heading>{aiIndex.metadata.total_products}</Heading>
              </TextContainer>
            </Stack>
            <Stack vertical spacing="extraTight">
              <TextContainer>
                <p><strong>Pages</strong></p>
                <Heading>{aiIndex.metadata.total_pages}</Heading>
              </TextContainer>
            </Stack>
            <Stack vertical spacing="extraTight">
              <TextContainer>
                <p><strong>Articles</strong></p>
                <Heading>{aiIndex.metadata.total_articles}</Heading>
              </TextContainer>
            </Stack>
          </Stack>
        </Stack>
      </Card>

      <Card sectioned>
        <Stack vertical spacing="tight">
          <Heading>Metadata</Heading>
          <TextContainer>
            <p><strong>Version:</strong> {aiIndex.version}</p>
            <p><strong>Generated:</strong> {new Date(aiIndex.metadata.generated_at).toLocaleString()}</p>
            <p><strong>Webhook URL:</strong> <code>{aiIndex.access.webhook_url}</code></p>
          </TextContainer>
        </Stack>
      </Card>

      <Card sectioned>
        <Stack vertical spacing="tight">
          <Heading>JSON Preview</Heading>
          <div style={{
            backgroundColor: '#f4f6f8',
            padding: '1rem',
            borderRadius: '4px',
            maxHeight: '400px',
            overflow: 'auto'
          }}>
            <pre style={{ margin: 0, fontSize: '12px' }}>
              {JSON.stringify(aiIndex, null, 2)}
            </pre>
          </div>
        </Stack>
      </Card>
    </Stack>
  );
}

export default AIIndexViewer;
