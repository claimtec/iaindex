/**
 * Base API client with authentication
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { AuthToken } from './types';

export class APIClient {
  private baseUrl: string;
  private axiosInstance: AxiosInstance;
  private authToken: string | null = null;
  private tokenExpiry: number | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.axiosInstance = axios.create({
      baseURL: baseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.axiosInstance.interceptors.request.use(
      async (config) => {
        // Check if token needs refresh
        if (this.authToken && this.isTokenExpired()) {
          await this.refreshAuth();
        }

        // Add auth header if token exists
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        // Retry on 401 with token refresh
        if (error.response?.status === 401 && !error.config._retry) {
          error.config._retry = true;
          await this.refreshAuth();
          return this.axiosInstance(error.config);
        }

        return Promise.reject(error);
      }
    );
  }

  /**
   * Authenticate with the API
   */
  async authenticate(username: string = 'admin', password: string = 'changeme'): Promise<void> {
    try {
      const response = await axios.post<AuthToken>(
        `${this.baseUrl}/v1/auth/login`,
        null,
        {
          params: { username, password },
        }
      );

      this.authToken = response.data.accessToken;
      // Set expiry to 90% of actual expiry to refresh before it expires
      this.tokenExpiry = Date.now() + (response.data.expiresIn * 1000 * 0.9);
    } catch (error: any) {
      throw new Error(`Authentication failed: ${error.response?.data?.error || error.message}`);
    }
  }

  /**
   * Check if token is expired
   */
  private isTokenExpired(): boolean {
    if (!this.tokenExpiry) return true;
    return Date.now() >= this.tokenExpiry;
  }

  /**
   * Refresh authentication token
   */
  private async refreshAuth(): Promise<void> {
    this.authToken = null;
    this.tokenExpiry = null;
    await this.authenticate();
  }

  /**
   * Make a GET request
   */
  async get<T = any>(path: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.get<T>(path, config);
    return response.data;
  }

  /**
   * Make a POST request
   */
  async post<T = any>(path: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.post<T>(path, data, config);
    return response.data;
  }

  /**
   * Make a PUT request
   */
  async put<T = any>(path: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.put<T>(path, data, config);
    return response.data;
  }

  /**
   * Make a DELETE request
   */
  async delete<T = any>(path: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.delete<T>(path, config);
    return response.data;
  }

  /**
   * Set custom API key for authentication
   */
  setApiKey(apiKey: string): void {
    this.axiosInstance.defaults.headers['X-API-Key'] = apiKey;
  }

  /**
   * Get the axios instance for custom requests
   */
  getAxiosInstance(): AxiosInstance {
    return this.axiosInstance;
  }
}
