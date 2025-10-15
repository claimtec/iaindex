import React, { useState, useEffect } from 'react';
import {
  Card,
  Stack,
  TextContainer,
  Heading,
  Button,
  Badge,
  TextStyle,
  Icon,
} from '@shopify/polaris';
import { CircleTickMajor, CircleAlertMajor } from '@shopify/polaris-icons';

function VerificationBadge() {
  const [verification, setVerification] = useState({
    domain: 'pending',
    c2pa: 'pending',
    merkle: 'pending',
    lastUpdated: null,
  });
  const [analytics, setAnalytics] = useState({
    totalReceipts: 0,
    allowedCount: 0,
    deniedCount: 0,
    policyViolations: 0,
  });
  const [loading, setLoading] = useState(false);
  const [showEmbed, setShowEmbed] = useState(false);

  useEffect(() => {
    fetchVerificationStatus();
    fetchReceiptAnalytics();
  }, []);

  const fetchVerificationStatus = async () => {
    try {
      const response = await fetch('/api/verification-status');
      const data = await response.json();
      if (data.success) {
        setVerification(data.verification);
      }
    } catch (err) {
      console.error('Error fetching verification:', err);
    }
  };

  const fetchReceiptAnalytics = async () => {
    try {
      const response = await fetch('/api/receipt-analytics?range=7d');
      const data = await response.json();
      if (data.success) {
        setAnalytics(data.analytics);
      }
    } catch (err) {
      console.error('Error fetching analytics:', err);
    }
  };

  const handleVerify = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/verify-domain', { method: 'POST' });
      const data = await response.json();
      if (data.success) {
        await fetchVerificationStatus();
      }
    } catch (err) {
      console.error('Error verifying domain:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyEmbedCode = () => {
    const code = `<div id="aiindex-badge"></div>
<script src="https://cdn.aiindex.org/badge.js" data-domain="${window.location.hostname}"></script>`;
    navigator.clipboard.writeText(code);
  };

  const VerificationCard = ({ title, status }) => (
    <Card sectioned>
      <Stack vertical spacing="tight" alignment="center">
        <Icon
          source={status === 'verified' ? CircleTickMajor : CircleAlertMajor}
          color={status === 'verified' ? 'success' : 'warning'}
        />
        <Heading>{title}</Heading>
        <Badge status={status === 'verified' ? 'success' : 'warning'}>
          {status === 'verified' ? 'Verified' : 'Pending'}
        </Badge>
      </Stack>
    </Card>
  );

  return (
    <Stack vertical>
      <Card sectioned title="Verification Status (v1.1)">
        <TextContainer>
          <p>View live verification status and analytics for your AI Index.</p>
        </TextContainer>
      </Card>

      <Card>
        <Card.Section>
          <Stack distribution="fillEvenly">
            <VerificationCard title="Domain Verification" status={verification.domain} />
            <VerificationCard title="C2PA Provenance" status={verification.c2pa} />
            <VerificationCard title="Merkle Attestation" status={verification.merkle} />
          </Stack>
        </Card.Section>

        {verification.lastUpdated && (
          <Card.Section>
            <TextStyle variation="subdued">
              Last updated: {new Date(verification.lastUpdated).toLocaleString()}
            </TextStyle>
          </Card.Section>
        )}
      </Card>

      <Card sectioned title="Receipt Analytics (Last 7 Days)">
        <Stack distribution="fillEvenly">
          <Stack vertical spacing="tight" alignment="center">
            <Heading>Total Receipts</Heading>
            <TextStyle variation="positive">{analytics.totalReceipts}</TextStyle>
          </Stack>
          <Stack vertical spacing="tight" alignment="center">
            <Heading>Allowed</Heading>
            <TextStyle variation="positive">{analytics.allowedCount}</TextStyle>
          </Stack>
          <Stack vertical spacing="tight" alignment="center">
            <Heading>Denied</Heading>
            <TextStyle variation="negative">{analytics.deniedCount}</TextStyle>
          </Stack>
          <Stack vertical spacing="tight" alignment="center">
            <Heading>Violations</Heading>
            <TextStyle variation="warning">{analytics.policyViolations}</TextStyle>
          </Stack>
        </Stack>
      </Card>

      <Card sectioned title="Quick Actions">
        <Stack spacing="tight">
          <Button primary onClick={handleVerify} loading={loading}>
            Verify Domain
          </Button>
          <Button onClick={() => window.open(`https://aiindex.org/dashboard?domain=${window.location.hostname}`, '_blank')}>
            View Full Dashboard
          </Button>
          <Button onClick={() => setShowEmbed(!showEmbed)}>
            {showEmbed ? 'Hide' : 'Show'} Embed Code
          </Button>
        </Stack>
      </Card>

      {showEmbed && (
        <Card sectioned title="Badge Embed Code">
          <TextContainer>
            <p>Copy this code to display the verification badge on your storefront:</p>
            <textarea
              readOnly
              style={{
                width: '100%',
                padding: '10px',
                fontFamily: 'monospace',
                fontSize: '12px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                minHeight: '80px',
              }}
              value={`<div id="aiindex-badge"></div>
<script src="https://cdn.aiindex.org/badge.js" data-domain="${window.location.hostname}"></script>`}
            />
            <Button onClick={copyEmbedCode}>Copy to Clipboard</Button>
          </TextContainer>
        </Card>
      )}

      <Card sectioned>
        <Stack vertical spacing="tight">
          <Heading>External Dashboard</Heading>
          <TextContainer>
            <p>
              View detailed analytics, policy enforcement metrics, and compliance reports
              on the AIIndex dashboard.
            </p>
            <Button
              primary
              external
              url={`https://aiindex.org/dashboard?domain=${window.location.hostname}`}
            >
              Open Dashboard
            </Button>
          </TextContainer>
        </Stack>
      </Card>
    </Stack>
  );
}

export default VerificationBadge;
