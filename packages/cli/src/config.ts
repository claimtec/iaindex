import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

export interface Config {
  apiBaseUrl: string;
  token?: string;
  userId?: string;
}

const CONFIG_DIR = path.join(os.homedir(), '.iaindex');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

export const DEFAULT_CONFIG: Config = {
  apiBaseUrl: 'https://api.iaindex.org'
};

export function ensureConfigDir(): void {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
}

export function loadConfig(): Config {
  ensureConfigDir();

  if (fs.existsSync(CONFIG_FILE)) {
    try {
      const data = fs.readFileSync(CONFIG_FILE, 'utf-8');
      return { ...DEFAULT_CONFIG, ...JSON.parse(data) };
    } catch (error) {
      return DEFAULT_CONFIG;
    }
  }

  return DEFAULT_CONFIG;
}

export function saveConfig(config: Config): void {
  ensureConfigDir();
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf-8');
}

export function getConfigPath(): string {
  return CONFIG_FILE;
}
