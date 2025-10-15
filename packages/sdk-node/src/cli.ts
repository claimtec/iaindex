#!/usr/bin/env node
/**
 * AIIndex CLI tool - aiindex-gen
 */

import { Command } from 'commander';
import * as fs from 'fs/promises';
import * as path from 'path';
import chalk from 'chalk';
import ora from 'ora';
import { AIIndexGenerator } from './generator';
import { SignatureManager } from './signer';
import { ReceiptHandler } from './receipts';
import { Validator } from './validator';
import type { CLIConfig, AIIndexFile } from './types';

const program = new Command();

program
  .name('aiindex-gen')
  .description('AIIndex CLI tool for generating and managing AI Index files')
  .version('1.0.0');

/**
 * Init command - Create configuration file
 */
program
  .command('init')
  .description('Create a new aiindex.config.json file')
  .option('-o, --output <path>', 'Output path for config file', './aiindex.config.json')
  .action(async (options) => {
    const spinner = ora('Creating configuration file...').start();

    try {
      const config: CLIConfig = {
        version: '1.0',
        name: 'My AI Service',
        description: 'A powerful AI service',
        url: 'https://example.com',
        capabilities: ['natural-language-processing', 'machine-learning'],
        categories: ['ai', 'nlp'],
        outputPath: './ai-index.json',
        privateKeyPath: './keys/private-key.json',
        publicKeyPath: './keys/public-key.json',
        apiEndpoint: 'https://api.aiindex.com',
        webhookPort: 3000,
        webhookPath: '/webhook/receipts',
      };

      await fs.writeFile(options.output, JSON.stringify(config, null, 2));
      spinner.succeed(chalk.green(`Configuration file created at ${options.output}`));

      console.log(chalk.cyan('\nNext steps:'));
      console.log(chalk.white('1. Edit aiindex.config.json with your service details'));
      console.log(chalk.white('2. Run "aiindex-gen build" to generate your AI Index file'));
      console.log(chalk.white('3. Run "aiindex-gen sign" to add a cryptographic signature'));
    } catch (error) {
      spinner.fail(chalk.red('Failed to create configuration file'));
      console.error(error);
      process.exit(1);
    }
  });

/**
 * Build command - Generate ai-index.json
 */
program
  .command('build')
  .description('Generate ai-index.json from website or configuration')
  .option('-c, --config <path>', 'Path to configuration file', './aiindex.config.json')
  .option('-u, --url <url>', 'Website URL to crawl')
  .option('-o, --output <path>', 'Output path for AI Index file')
  .option('--no-crawl', 'Skip website crawling, use config only')
  .action(async (options) => {
    const spinner = ora('Generating AI Index file...').start();

    try {
      // Load configuration if exists
      let config: Partial<CLIConfig> = {};
      try {
        const configData = await fs.readFile(options.config, 'utf-8');
        config = JSON.parse(configData);
      } catch {
        if (!options.url) {
          spinner.fail(chalk.red('No configuration file found and no URL provided'));
          console.log(chalk.yellow('Run "aiindex-gen init" to create a configuration file'));
          process.exit(1);
        }
      }

      const baseUrl = options.url || config.url;
      if (!baseUrl) {
        spinner.fail(chalk.red('No URL specified in config or command line'));
        process.exit(1);
      }

      spinner.text = `Crawling ${baseUrl}...`;

      // Generate AI Index
      const generator = new AIIndexGenerator({
        baseUrl,
        config: {
          version: config.version,
          name: config.name,
          description: config.description,
          url: config.url,
          capabilities: config.capabilities,
          categories: config.categories,
        },
      });

      const aiIndex = options.crawl !== false
        ? await generator.generate()
        : {
            version: config.version || '1.0',
            name: config.name || 'Unknown',
            description: config.description || '',
            url: config.url || baseUrl,
            capabilities: config.capabilities || [],
            categories: config.categories || [],
            generated: new Date().toISOString(),
          };

      // Write to file
      const outputPath = options.output || config.outputPath || './ai-index.json';
      await fs.writeFile(outputPath, JSON.stringify(aiIndex, null, 2));

      spinner.succeed(chalk.green(`AI Index file generated at ${outputPath}`));

      // Show summary
      console.log(chalk.cyan('\nGenerated AI Index:'));
      console.log(chalk.white(`  Name: ${aiIndex.name}`));
      console.log(chalk.white(`  Description: ${aiIndex.description}`));
      console.log(chalk.white(`  Capabilities: ${aiIndex.capabilities?.join(', ') || 'None'}`));
      console.log(chalk.white(`  Categories: ${aiIndex.categories?.join(', ') || 'None'}`));
    } catch (error) {
      spinner.fail(chalk.red('Failed to generate AI Index file'));
      console.error(error);
      process.exit(1);
    }
  });

/**
 * Verify command - Validate AI Index file
 */
program
  .command('verify')
  .description('Validate ai-index.json file')
  .argument('[file]', 'Path to AI Index file', './ai-index.json')
  .option('--check-signature', 'Verify cryptographic signature')
  .action(async (file, options) => {
    const spinner = ora('Validating AI Index file...').start();

    try {
      const data = await fs.readFile(file, 'utf-8');
      const aiIndex: AIIndexFile = JSON.parse(data);

      // Validate schema
      const validator = new Validator();
      const result = validator.validate(aiIndex);

      if (result.valid) {
        spinner.succeed(chalk.green('AI Index file is valid'));

        if (result.warnings && result.warnings.length > 0) {
          console.log(chalk.yellow('\nWarnings:'));
          result.warnings.forEach(warning => {
            console.log(chalk.yellow(`  - ${warning.field}: ${warning.message}`));
          });
        }

        // Verify signature if requested
        if (options.checkSignature && aiIndex.signature) {
          spinner.start('Verifying signature...');
          const signer = new SignatureManager();
          const isValid = await signer.verifyFile(aiIndex);

          if (isValid) {
            spinner.succeed(chalk.green('Signature is valid'));
          } else {
            spinner.fail(chalk.red('Signature verification failed'));
            process.exit(1);
          }
        } else if (options.checkSignature) {
          console.log(chalk.yellow('\nNo signature found in file'));
        }
      } else {
        spinner.fail(chalk.red('AI Index file is invalid'));

        if (result.errors) {
          console.log(chalk.red('\nErrors:'));
          result.errors.forEach(error => {
            console.log(chalk.red(`  - ${error.field}: ${error.message} (${error.code})`));
          });
        }

        process.exit(1);
      }
    } catch (error) {
      spinner.fail(chalk.red('Failed to validate AI Index file'));
      console.error(error);
      process.exit(1);
    }
  });

/**
 * Sign command - Add cryptographic signature
 */
program
  .command('sign')
  .description('Add cryptographic signature to AI Index file')
  .argument('[file]', 'Path to AI Index file', './ai-index.json')
  .option('-k, --key <path>', 'Path to private key file')
  .option('--generate-keys', 'Generate new key pair')
  .option('--key-output <path>', 'Output directory for generated keys', './keys')
  .action(async (file, options) => {
    const spinner = ora('Signing AI Index file...').start();

    try {
      // Load AI Index file
      const data = await fs.readFile(file, 'utf-8');
      const aiIndex: AIIndexFile = JSON.parse(data);

      const signer = new SignatureManager();

      if (options.generateKeys) {
        spinner.text = 'Generating key pair...';

        // Generate new key pair
        const keyPair = await signer.generateKeyPair({ keyFormat: 'jwk' });

        // Create keys directory
        await fs.mkdir(options.keyOutput, { recursive: true });

        // Save keys
        const privateKeyPath = path.join(options.keyOutput, 'private-key.json');
        const publicKeyPath = path.join(options.keyOutput, 'public-key.json');

        await fs.writeFile(privateKeyPath, keyPair.privateKey);
        await fs.writeFile(publicKeyPath, keyPair.publicKey);

        console.log(chalk.green(`\nKey pair generated:`));
        console.log(chalk.white(`  Private key: ${privateKeyPath}`));
        console.log(chalk.white(`  Public key: ${publicKeyPath}`));
        console.log(chalk.yellow('\n  IMPORTANT: Keep your private key secure!'));

        spinner.text = 'Signing AI Index file...';
      } else if (options.key) {
        // Load private key from file
        const privateKey = await fs.readFile(options.key, 'utf-8');
        await signer.loadPrivateKey(privateKey);

        // Try to load public key from same directory
        const publicKeyPath = options.key.replace('private', 'public');
        try {
          const publicKey = await fs.readFile(publicKeyPath, 'utf-8');
          await signer.loadPublicKey(publicKey);
        } catch {
          spinner.fail(chalk.red('Public key not found'));
          console.log(chalk.yellow(`Expected public key at: ${publicKeyPath}`));
          process.exit(1);
        }
      } else {
        spinner.fail(chalk.red('No private key provided'));
        console.log(chalk.yellow('Use --key <path> to specify private key or --generate-keys to create new keys'));
        process.exit(1);
      }

      // Sign the file
      const signedAiIndex = await signer.signFile(aiIndex);

      // Save signed file
      await fs.writeFile(file, JSON.stringify(signedAiIndex, null, 2));

      spinner.succeed(chalk.green(`AI Index file signed successfully`));
      console.log(chalk.cyan('\nSignature added to file'));
    } catch (error) {
      spinner.fail(chalk.red('Failed to sign AI Index file'));
      console.error(error);
      process.exit(1);
    }
  });

/**
 * Serve command - Start webhook server
 */
program
  .command('serve')
  .description('Start local webhook server to receive receipts')
  .option('-p, --port <port>', 'Port to listen on', '3000')
  .option('--path <path>', 'Webhook endpoint path', '/webhook/receipts')
  .option('-c, --config <path>', 'Path to configuration file', './aiindex.config.json')
  .option('--api-key <key>', 'API key for authentication')
  .option('--forward', 'Forward receipts to AIIndex API')
  .action(async (options) => {
    const spinner = ora('Starting webhook server...').start();

    try {
      // Load configuration if exists
      let config: Partial<CLIConfig> = {};
      try {
        const configData = await fs.readFile(options.config, 'utf-8');
        config = JSON.parse(configData);
      } catch {
        // Config file is optional for serve command
      }

      const port = parseInt(options.port) || config.webhookPort || 3000;
      const webhookPath = options.path || config.webhookPath || '/webhook/receipts';
      const apiEndpoint = config.apiEndpoint || 'https://api.aiindex.com';

      const handler = new ReceiptHandler({
        apiEndpoint,
        autoForward: options.forward || false,
      });

      await handler.startWebhookServer({
        port,
        path: webhookPath,
        apiKey: options.apiKey,
        onReceipt: async (receipt) => {
          console.log(chalk.cyan('\nReceipt received:'));
          console.log(chalk.white(`  ID: ${receipt.id}`));
          console.log(chalk.white(`  Agent: ${receipt.agentId}`));
          console.log(chalk.white(`  Action: ${receipt.action}`));
          console.log(chalk.white(`  Timestamp: ${receipt.timestamp}`));
        },
      });

      spinner.succeed(chalk.green('Webhook server started'));
      console.log(chalk.cyan(`\nListening on port ${port}`));
      console.log(chalk.white(`Endpoint: http://localhost:${port}${webhookPath}`));

      if (options.forward) {
        console.log(chalk.yellow('\nAuto-forwarding enabled - receipts will be sent to AIIndex API'));
      }

      // Keep process running
      process.on('SIGINT', () => {
        console.log(chalk.yellow('\n\nShutting down...'));
        process.exit(0);
      });
    } catch (error) {
      spinner.fail(chalk.red('Failed to start webhook server'));
      console.error(error);
      process.exit(1);
    }
  });

// Parse command line arguments
program.parse();
