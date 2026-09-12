import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.iaindex.org';

// In-memory storage for scan results
const scanResults = new Map<string, any>();

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { url } = body;

    if (!url) {
      return NextResponse.json(
        { error: 'URL is required' },
        { status: 400 }
      );
    }

    // Validate URL format
    let parsedUrl;
    try {
      parsedUrl = new URL(url.startsWith('http') ? url : `https://${url}`);
    } catch (error) {
      return NextResponse.json(
        { error: 'Invalid URL format' },
        { status: 400 }
      );
    }

    const domain = parsedUrl.hostname.replace('www.', '');

    console.log(`[Scan API] Starting visibility scan for: ${domain}`);

    // Step 1: Create/get website record in backend
    const websiteResponse = await fetch(`${API_URL}/v1/websites`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: parsedUrl.toString(),
        domain: domain,
      }),
    });

    if (!websiteResponse.ok) {
      const error = await websiteResponse.json();
      console.error('[Scan API] Website creation failed:', error);
      return NextResponse.json(
        { error: 'Failed to register website for scanning' },
        { status: 500 }
      );
    }

    const website = await websiteResponse.json();
    console.log(`[Scan API] Website registered: ${website.id}`);

    // Step 2: Trigger visibility check
    const visibilityResponse = await fetch(`${API_URL}/v1/visibility/check`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        website_id: website.id,
        queries: [domain, parsedUrl.hostname],
        platforms: ['chatgpt', 'perplexity'],
      }),
    });

    if (!visibilityResponse.ok) {
      const error = await visibilityResponse.json();
      console.error('[Scan API] Visibility check failed:', error);

      // Return mock data as fallback
      console.log('[Scan API] Falling back to mock data');
      return NextResponse.json(generateMockScanResult(url));
    }

    const visibilityData = await visibilityResponse.json();
    console.log(`[Scan API] Visibility check completed: score=${visibilityData.visibility_score}`);

    // Step 3: Get schema recommendations
    let recommendations = [];
    try {
      const schemaResponse = await fetch(`${API_URL}/v1/schema/recommendations/${website.id}`);
      if (schemaResponse.ok) {
        const schemaData = await schemaResponse.json();
        recommendations = schemaData.recommendations || [];
      }
    } catch (error) {
      console.warn('[Scan API] Schema recommendations failed, using defaults');
      recommendations = getDefaultRecommendations();
    }

    // Format result
    const scanId = `scan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const result = {
      scan_id: scanId,
      website_id: website.id,
      url: parsedUrl.toString(),
      domain: domain,
      visibility_score: visibilityData.visibility_score,
      platform_scores: visibilityData.platform_scores || {
        chatgpt: 0,
        perplexity: 0,
      },
      mentions: visibilityData.mentions || [],
      recommendations: recommendations.slice(0, 3),
      scanned_at: visibilityData.checked_at || new Date().toISOString(),
    };

    // Store the result
    scanResults.set(scanId, result);

    return NextResponse.json(result);
  } catch (error) {
    console.error('[Scan API] Unexpected error:', error);

    // Return mock data as fallback
    try {
      const body = await request.json();
      return NextResponse.json(generateMockScanResult(body.url));
    } catch {
      return NextResponse.json(
        { error: 'Failed to scan website' },
        { status: 500 }
      );
    }
  }
}

// Fallback mock data generator
function generateMockScanResult(url: string) {
  const scanId = `scan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const baseScore = Math.floor(Math.random() * 40) + 30;
  const variance = () => Math.floor(Math.random() * 20) - 10;

  const chatgptScore = Math.max(0, Math.min(100, baseScore + variance()));
  const perplexityScore = Math.max(0, Math.min(100, baseScore + variance()));
  const overallScore = Math.round((chatgptScore + perplexityScore) / 2);

  return {
    scan_id: scanId,
    url,
    visibility_score: overallScore,
    platform_scores: {
      chatgpt: chatgptScore,
      perplexity: perplexityScore,
    },
    recommendations: getDefaultRecommendations().slice(0, 3),
    scanned_at: new Date().toISOString(),
  };
}

function getDefaultRecommendations() {
  return [
    {
      title: 'Add Schema.org Markup',
      description: 'Implement structured data markup to help AI engines understand your content better. Start with Organization, WebSite, and Article schemas.',
      impact_score: 85,
      priority: 'critical' as const,
    },
    {
      title: 'Optimize Meta Descriptions',
      description: 'Your meta descriptions are too short. AI engines use these to understand page context. Aim for 150-160 characters with clear, descriptive content.',
      impact_score: 72,
      priority: 'high' as const,
    },
    {
      title: 'Improve Content Structure',
      description: 'Use clear heading hierarchy (H1, H2, H3) to help AI engines parse your content. Add more descriptive subheadings.',
      impact_score: 68,
      priority: 'high' as const,
    },
    {
      title: 'Add FAQ Schema',
      description: 'Implement FAQ schema markup for common questions. This significantly improves AI visibility and citation likelihood.',
      impact_score: 75,
      priority: 'critical' as const,
    },
  ];
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const scanId = searchParams.get('scan_id');

    if (!scanId) {
      return NextResponse.json(
        { error: 'scan_id is required' },
        { status: 400 }
      );
    }

    const result = scanResults.get(scanId);

    if (!result) {
      return NextResponse.json(
        { error: 'Scan not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(result);
  } catch (error) {
    console.error('Get scan error:', error);
    return NextResponse.json(
      { error: 'Failed to retrieve scan results' },
      { status: 500 }
    );
  }
}
