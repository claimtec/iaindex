import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import * as fs from 'fs';
import * as path from 'path';
import inquirer from 'inquirer';
import { signData } from '../crypto';

interface IndexConfig {
  url: string;
  title: string;
  description?: string;
  contentType: string;
  aiGenerated: {
    percentage: number;
    sections: string[];
  };
  humanOversight: {
    level: string;
    verifiedBy: string;
  };
  sources?: Array<{
    type: string;
    description: string;
  }>;
  timestamp: string;
  publisher: {
    name: string;
    domain: string;
    publicKey?: string;
  };
}

export function createIndexCommand(): Command {
  const indexCmd = new Command('create-index');
  indexCmd
    .description('Create an IAIndex attestation file')
    .argument('[config]', 'Path to config JSON file')
    .option('-i, --interactive', 'Interactive mode with prompts')
    .option('-o, --output <file>', 'Output file path', './iaindex.json')
    .option('-s, --sign <privateKey>', 'Path to private key for signing')
    .action(async (configPath: string | undefined, options) => {
      let config: IndexConfig;

      if (options.interactive || !configPath) {
        // Interactive mode
        console.log(chalk.cyan('\n📝 IAIndex Attestation Generator\n'));

        const answers = await inquirer.prompt([
          {
            type: 'input',
            name: 'url',
            message: 'Content URL:',
            validate: (input) => input.length > 0 || 'URL is required'
          },
          {
            type: 'input',
            name: 'title',
            message: 'Content Title:',
            validate: (input) => input.length > 0 || 'Title is required'
          },
          {
            type: 'input',
            name: 'description',
            message: 'Description (optional):'
          },
          {
            type: 'list',
            name: 'contentType',
            message: 'Content Type:',
            choices: ['article', 'blog-post', 'documentation', 'code', 'image', 'video', 'other']
          },
          {
            type: 'number',
            name: 'aiPercentage',
            message: 'AI-generated percentage (0-100):',
            default: 50,
            validate: (input) => (input >= 0 && input <= 100) || 'Must be between 0 and 100'
          },
          {
            type: 'input',
            name: 'aiSections',
            message: 'AI-generated sections (comma-separated):',
            default: 'content'
          },
          {
            type: 'list',
            name: 'oversightLevel',
            message: 'Human oversight level:',
            choices: ['full', 'partial', 'minimal', 'none']
          },
          {
            type: 'input',
            name: 'verifiedBy',
            message: 'Verified by:',
            validate: (input) => input.length > 0 || 'Verifier is required'
          },
          {
            type: 'input',
            name: 'publisherName',
            message: 'Publisher name:',
            validate: (input) => input.length > 0 || 'Publisher name is required'
          },
          {
            type: 'input',
            name: 'publisherDomain',
            message: 'Publisher domain:',
            validate: (input) => input.length > 0 || 'Publisher domain is required'
          },
          {
            type: 'input',
            name: 'publicKey',
            message: 'Public key (optional, press Enter to skip):'
          }
        ]);

        config = {
          url: answers.url,
          title: answers.title,
          description: answers.description || undefined,
          contentType: answers.contentType,
          aiGenerated: {
            percentage: answers.aiPercentage,
            sections: answers.aiSections.split(',').map((s: string) => s.trim())
          },
          humanOversight: {
            level: answers.oversightLevel,
            verifiedBy: answers.verifiedBy
          },
          timestamp: new Date().toISOString(),
          publisher: {
            name: answers.publisherName,
            domain: answers.publisherDomain,
            publicKey: answers.publicKey || undefined
          }
        };
      } else {
        // Load from config file
        const spinner = ora('Loading configuration...').start();

        try {
          const configFilePath = path.resolve(configPath);
          const configData = fs.readFileSync(configFilePath, 'utf-8');
          config = JSON.parse(configData);

          // Add timestamp if not present
          if (!config.timestamp) {
            config.timestamp = new Date().toISOString();
          }

          spinner.succeed(chalk.green('Configuration loaded'));
        } catch (error: any) {
          spinner.fail(chalk.red('Failed to load configuration'));
          console.error(chalk.red(`Error: ${error.message}`));
          process.exit(1);
        }
      }

      // Build IAIndex object
      const iaindex: any = {
        version: '1.1',
        url: config.url,
        content: {
          title: config.title,
          description: config.description,
          type: config.contentType
        },
        aiGenerated: config.aiGenerated,
        humanOversight: config.humanOversight,
        timestamp: config.timestamp,
        publisher: config.publisher
      };

      if (config.sources) {
        iaindex.sources = config.sources;
      }

      // Sign if private key provided
      if (options.sign) {
        const spinner = ora('Signing attestation...').start();

        try {
          const privateKeyPath = path.resolve(options.sign);
          const privateKey = fs.readFileSync(privateKeyPath, 'utf-8');

          // Create canonical string for signing
          const dataToSign = JSON.stringify({
            url: iaindex.url,
            timestamp: iaindex.timestamp,
            aiPercentage: iaindex.aiGenerated.percentage
          });

          const signature = signData(dataToSign, privateKey);
          iaindex.signature = signature;

          spinner.succeed(chalk.green('Attestation signed'));
        } catch (error: any) {
          spinner.fail(chalk.red('Signing failed'));
          console.error(chalk.red(`Error: ${error.message}`));
          process.exit(1);
        }
      }

      // Write output file
      const outputPath = path.resolve(options.output);
      const spinner = ora('Writing IAIndex file...').start();

      try {
        fs.writeFileSync(outputPath, JSON.stringify(iaindex, null, 2), 'utf-8');
        spinner.succeed(chalk.green('IAIndex file created successfully!'));

        console.log('\n' + chalk.cyan('Output saved to:'));
        console.log(chalk.white(outputPath));

        console.log('\n' + chalk.cyan('IAIndex Content:'));
        console.log(chalk.white('━'.repeat(60)));
        console.log(chalk.gray(JSON.stringify(iaindex, null, 2)));
        console.log(chalk.white('━'.repeat(60)));

        console.log('\n' + chalk.green('✓ Next steps:'));
        console.log(chalk.gray('  1. Review the generated file'));
        console.log(chalk.gray('  2. Upload to your website at /.well-known/iaindex.json'));
        console.log(chalk.gray('  3. Submit to IAIndex registry'));
      } catch (error: any) {
        spinner.fail(chalk.red('Failed to write file'));
        console.error(chalk.red(`Error: ${error.message}`));
        process.exit(1);
      }
    });

  return indexCmd;
}
