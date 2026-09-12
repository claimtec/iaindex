import axios from 'axios';

// API client configuration
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interfaces
export interface ScanResult {
  scan_id: string;
  url: string;
  visibility_score: number;
  platform_scores: {
    chatgpt: number;
    perplexity: number;
    claude: number;
  };
  recommendations: Array<{
    title: string;
    description: string;
    impact_score: number;
    priority: 'critical' | 'high' | 'medium';
  }>;
  scanned_at: string;
}

export interface EmailSubmissionResponse {
  success: boolean;
  message: string;
}

/**
 * Scan a website for AI visibility
 * @param url - The website URL to scan
 * @returns Promise with scan results including scan_id
 */
export async function scanWebsite(url: string): Promise<ScanResult> {
  try {
    const response = await apiClient.post<ScanResult>('/scan', { url });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.error || error.message;
      throw new Error(`Failed to scan website: ${message}`);
    }
    throw new Error('An unexpected error occurred while scanning the website');
  }
}

/**
 * Get scan results by scan ID
 * @param scanId - The unique scan identifier
 * @returns Promise with scan results
 */
export async function getScanResults(scanId: string): Promise<ScanResult> {
  try {
    const response = await apiClient.get<ScanResult>(`/scan?scan_id=${scanId}`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error('Scan results not found');
      }
      const message = error.response?.data?.error || error.message;
      throw new Error(`Failed to retrieve scan results: ${message}`);
    }
    throw new Error('An unexpected error occurred while retrieving scan results');
  }
}

/**
 * Submit email to receive detailed report
 * @param scanId - The scan identifier
 * @param email - User's email address
 * @returns Promise with submission response
 */
export async function submitEmail(
  scanId: string,
  email: string
): Promise<EmailSubmissionResponse> {
  try {
    // TODO: Implement email submission endpoint when backend is ready
    // For now, simulate successful submission
    await new Promise(resolve => setTimeout(resolve, 1000));

    return {
      success: true,
      message: 'Email submitted successfully',
    };
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.error || error.message;
      throw new Error(`Failed to submit email: ${message}`);
    }
    throw new Error('An unexpected error occurred while submitting email');
  }
}

/**
 * Error handler for API calls
 * Provides user-friendly error messages
 */
export function handleApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.code === 'ECONNABORTED') {
      return 'Request timed out. Please try again.';
    }
    if (error.response) {
      return error.response.data?.error || 'An error occurred. Please try again.';
    }
    if (error.request) {
      return 'Unable to connect to the server. Please check your internet connection.';
    }
  }
  return 'An unexpected error occurred. Please try again.';
}

export default apiClient;
