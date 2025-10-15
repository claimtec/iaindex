import React, { useState, useEffect } from 'react';
import {
  Card,
  Stack,
  TextContainer,
  Heading,
  SettingToggle,
  Button,
  Banner,
  TextStyle,
} from '@shopify/polaris';

function PolicySettings() {
  const [settings, setSettings] = useState({
    blockTraining: false,
    allowRetrievalOnly: false,
    requireSignedReceipts: false,
    enableRenderFallback: false,
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/policy-settings');
      const data = await response.json();
      if (data.success) {
        setSettings(data.settings);
      }
    } catch (err) {
      console.error('Error fetching policy settings:', err);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    setSuccess(false);
    try {
      const response = await fetch('/api/policy-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
      const data = await response.json();
      if (data.success) {
        setSuccess(true);
        setTimeout(() => setSuccess(false), 3000);
      }
    } catch (err) {
      console.error('Error saving policy settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = (field) => {
    setSettings({ ...settings, [field]: !settings[field] });
  };

  return (
    <Stack vertical>
      {success && (
        <Banner status="success" onDismiss={() => setSuccess(false)}>
          <p>Policy settings saved successfully! AI Index and policy JSON have been regenerated.</p>
        </Banner>
      )}

      <Card sectioned title="AI Policy Controls (v1.1)">
        <TextContainer>
          <p>Configure how AI systems can interact with your store content.</p>
        </TextContainer>
      </Card>

      <Card sectioned>
        <SettingToggle
          action={{
            content: settings.blockTraining ? 'Enabled' : 'Disabled',
            onAction: () => handleToggle('blockTraining'),
          }}
          enabled={settings.blockTraining}
        >
          <Stack vertical spacing="tight">
            <Heading>Block Model Training</Heading>
            <TextStyle variation="subdued">
              Prevent AI systems from using your content for model training.
              Sets policy.training="block".
            </TextStyle>
          </Stack>
        </SettingToggle>
      </Card>

      <Card sectioned>
        <SettingToggle
          action={{
            content: settings.allowRetrievalOnly ? 'Enabled' : 'Disabled',
            onAction: () => handleToggle('allowRetrievalOnly'),
          }}
          enabled={settings.allowRetrievalOnly}
        >
          <Stack vertical spacing="tight">
            <Heading>Allow Retrieval Only</Heading>
            <TextStyle variation="subdued">
              Block training but allow retrieval for RAG/search.
              Sets policy.training="block", policy.retrieval="allow".
            </TextStyle>
          </Stack>
        </SettingToggle>
      </Card>

      <Card sectioned>
        <SettingToggle
          action={{
            content: settings.requireSignedReceipts ? 'Enabled' : 'Disabled',
            onAction: () => handleToggle('requireSignedReceipts'),
          }}
          enabled={settings.requireSignedReceipts}
        >
          <Stack vertical spacing="tight">
            <Heading>Require Signed Receipts</Heading>
            <TextStyle variation="subdued">
              Require cryptographic signatures on all indexing receipts.
              Sets receipts.require_signed=true.
            </TextStyle>
          </Stack>
        </SettingToggle>
      </Card>

      <Card sectioned>
        <SettingToggle
          action={{
            content: settings.enableRenderFallback ? 'Enabled' : 'Disabled',
            onAction: () => handleToggle('enableRenderFallback'),
          }}
          enabled={settings.enableRenderFallback}
        >
          <Stack vertical spacing="tight">
            <Heading>Enable Render Fallback</Heading>
            <TextStyle variation="subdued">
              Enable edge rendering for dynamic content.
              Sets render_fallback.mode="edge".
            </TextStyle>
          </Stack>
        </SettingToggle>
      </Card>

      <Card sectioned>
        <Stack vertical spacing="tight">
          <Heading>Generated Files</Heading>
          <TextContainer>
            <p><code>/ai-index.json</code></p>
            <p><code>/.well-known/aiindex-policy.json</code></p>
            <TextStyle variation="subdued">
              Policy settings are saved to both files automatically.
            </TextStyle>
          </TextContainer>
        </Stack>
      </Card>

      <Card sectioned>
        <Stack distribution="trailing">
          <Button primary onClick={handleSave} loading={loading}>
            Save Policy Settings
          </Button>
        </Stack>
      </Card>
    </Stack>
  );
}

export default PolicySettings;
