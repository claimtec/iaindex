import axios, { AxiosInstance } from 'axios';
import { loadConfig, saveConfig } from './config';

export class IAIndexAPI {
  private client: AxiosInstance;
  private config = loadConfig();

  constructor() {
    this.client = axios.create({
      baseURL: this.config.apiBaseUrl,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Add auth token if available
    if (this.config.token) {
      this.client.defaults.headers.common['Authorization'] = `Bearer ${this.config.token}`;
    }
  }

  async login(email: string, password: string): Promise<{ token: string; userId: string }> {
    const response = await this.client.post('/v1/auth/login', {
      email,
      password
    });

    const { access_token, user_id } = response.data;

    // Save token to config
    this.config.token = access_token;
    this.config.userId = user_id;
    saveConfig(this.config);

    // Update client headers
    this.client.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

    return { token: access_token, userId: user_id };
  }

  async verifyDomain(domain: string): Promise<{
    verification_token: string;
    dns_record: {
      name: string;
      value: string;
      type: string;
    };
  }> {
    const response = await this.client.post('/v1/publishers/verify', {
      domain,
      method: 'dns'
    });

    return response.data;
  }

  async checkVerification(token: string): Promise<{
    status: string;
    domain: string;
    verified: boolean;
  }> {
    const response = await this.client.get(`/v1/publishers/verify/${token}`);
    return response.data;
  }

  async createAttestation(data: any): Promise<any> {
    const response = await this.client.post('/v1/attestations', data);
    return response.data;
  }

  async getPublisher(domain: string): Promise<any> {
    const response = await this.client.get(`/v1/publishers/${domain}`);
    return response.data;
  }
}

export function createAPIClient(): IAIndexAPI {
  return new IAIndexAPI();
}
