import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import * as fs from 'fs';
import * as path from 'path';
import { generateKeyPair } from '../crypto';

export function createKeysCommand(): Command {
  const keys = new Command('generate-keys');
  keys
    .description('Generate RSA key pair for signing attestations')
    .option('-o, --output <dir>', 'Output directory for keys', process.cwd())
    .option('-n, --name <name>', 'Base name for key files', 'iaindex')
    .action(async (options) => {
      const spinner = ora('Generating RSA key pair...').start();

      try {
        const keyPair = generateKeyPair();
        const outputDir = path.resolve(options.output);

        // Ensure output directory exists
        if (!fs.existsSync(outputDir)) {
          fs.mkdirSync(outputDir, { recursive: true });
        }

        const privateKeyPath = path.join(outputDir, `${options.name}-private.pem`);
        const publicKeyPath = path.join(outputDir, `${options.name}-public.pem`);

        // Write keys to files
        fs.writeFileSync(privateKeyPath, keyPair.privateKey, 'utf-8');
        fs.writeFileSync(publicKeyPath, keyPair.publicKey, 'utf-8');

        // Set proper permissions on private key (Unix-like systems)
        if (process.platform !== 'win32') {
          fs.chmodSync(privateKeyPath, 0o600);
        }

        spinner.succeed(chalk.green('Key pair generated successfully!'));

        console.log('\n' + chalk.cyan('Keys saved to:'));
        console.log(chalk.white('━'.repeat(60)));
        console.log(chalk.yellow('Private Key: ') + chalk.white(privateKeyPath));
        console.log(chalk.yellow('Public Key:  ') + chalk.white(publicKeyPath));
        console.log(chalk.white('━'.repeat(60)));

        console.log('\n' + chalk.red('⚠ IMPORTANT: Keep your private key secure!'));
        console.log(chalk.gray('Never share or commit your private key to version control.'));
        console.log(chalk.gray('Use the public key in your IAIndex attestations.'));

        // Display public key for easy copying
        console.log('\n' + chalk.cyan('Public Key Content:'));
        console.log(chalk.white(keyPair.publicKey));
      } catch (error: any) {
        spinner.fail(chalk.red('Key generation failed'));
        console.error(chalk.red(`Error: ${error.message}`));
        process.exit(1);
      }
    });

  return keys;
}
