/**
 * AIIndex v1.1 Render Fallback Support
 */

import axios, { AxiosInstance } from 'axios';
import type { RenderResponse, RenderFallback } from './types';

export class RenderFallbackAdapter {
  private client: AxiosInstance;

  constructor(timeout: number = 30000) {
    this.client = axios.create({
      timeout,
      headers: {
        'Accept': 'application/json',
        'X-AIIndex-Version': 'v1.1',
      },
    });
  }

  /**
   * Fetch rendered content when ai-index.json is not available
   * Calls /render/snapshot endpoint
   */
  async fetchRenderedContent(
    domain: string,
    url?: string,
    clientId?: string,
    intent?: 'training' | 'retrieval'
  ): Promise<RenderResponse | null> {
    try {
      const renderUrl = url || `https://${domain}/render/snapshot`;

      const headers: Record<string, string> = {
        'X-AIIndex-Version': 'v1.1',
      };

      if (clientId) {
        headers['X-AIIndex-Client-ID'] = clientId;
      }

      if (intent) {
        headers['X-AIIndex-Intent'] = intent;
      }

      const response = await this.client.get<RenderResponse>(renderUrl, { headers });

      if (response.status === 200 && response.data) {
        return response.data;
      }

      return null;
    } catch (error) {
      console.error('Failed to fetch rendered content:', error);
      return null;
    }
  }

  /**
   * Try to fetch rendered content based on render_fallback settings
   */
  async tryRenderFallback(
    domain: string,
    renderFallback: RenderFallback | undefined,
    clientId?: string,
    intent?: 'training' | 'retrieval'
  ): Promise<RenderResponse | null> {
    if (!renderFallback?.enabled) {
      return null;
    }

    // Skip if mode is 'none'
    if (renderFallback.mode === 'none') {
      return null;
    }

    // Use custom endpoint if provided
    const endpoint = renderFallback.endpoint || `https://${domain}/render/snapshot`;

    return this.fetchRenderedContent(domain, endpoint, clientId, intent);
  }

  /**
   * Convert rendered content to a simple text format
   */
  extractText(renderResponse: RenderResponse): string {
    if (renderResponse.rendered_text) {
      return renderResponse.rendered_text;
    }

    if (renderResponse.rendered_html) {
      // Basic HTML to text conversion (strip tags)
      return renderResponse.rendered_html
        .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
        .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '')
        .replace(/<[^>]+>/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
    }

    return '';
  }

  /**
   * Check if render fallback is available for a domain
   */
  async probeRenderEndpoint(domain: string): Promise<boolean> {
    try {
      const renderUrl = `https://${domain}/render/snapshot`;
      const response = await this.client.head(renderUrl);
      return response.status === 200;
    } catch {
      return false;
    }
  }

  /**
   * Get metadata from render response
   */
  getMetadata(renderResponse: RenderResponse): Record<string, any> {
    return {
      url: renderResponse.url,
      rendered_at: renderResponse.metadata?.rendered_at,
      cache_ttl: renderResponse.metadata?.cache_ttl,
      source: 'render-fallback',
      ...renderResponse.metadata,
    };
  }
}
