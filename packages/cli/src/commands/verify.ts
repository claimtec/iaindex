import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { createAPIClient } from '../api';

export function createVerifyCommand(): Command {
  const verify = new Command('verify');
  verify.description('Domain verification commands');

  // Verify init command
  verify
    .command('init <domain>')
    .description('Initialize domain verification')
    .action(async (domain: string) => {
      const spinner = ora('Initiating domain verification...').start();

      try {
        const api = createAPIClient();
        const result = await api.verifyDomain(domain);

        spinner.succeed(chalk.green(`Verification initiated for ${chalk.bold(domain)}`));

        console.log('\n' + chalk.cyan('Add this TXT record to your DNS:'));
        console.log('\n' + chalk.white('━'.repeat(60)));
        console.log(chalk.yellow('Name:  ') + chalk.white(result.dns_record.name));
        console.log(chalk.yellow('Type:  ') + chalk.white(result.dns_record.type));
        console.log(chalk.yellow('Value: ') + chalk.white(result.dns_record.value));
        console.log(chalk.white('━'.repeat(60)));

        console.log('\n' + chalk.cyan('Verification Token:'));
        console.log(chalk.white(result.verification_token));

        console.log('\n' + chalk.gray('Then run: ') + chalk.green(`iaindex verify check ${result.verification_token}`));
      } catch (error: any) {
        spinner.fail(chalk.red('Verification initiation failed'));
        if (error.response) {
          console.error(chalk.red(`Error: ${error.response.data.detail || error.message}`));
        } else {
          console.error(chalk.red(`Error: ${error.message}`));
        }
        process.exit(1);
      }
    });

  // Verify check command
  verify
    .command('check <token>')
    .description('Check domain verification status')
    .action(async (token: string) => {
      const spinner = ora('Checking verification status...').start();

      try {
        const api = createAPIClient();
        const result = await api.checkVerification(token);

        if (result.verified) {
          spinner.succeed(chalk.green(`Domain ${chalk.bold(result.domain)} is verified!`));
        } else {
          spinner.warn(chalk.yellow(`Domain ${chalk.bold(result.domain)} is not yet verified`));
          console.log(chalk.gray(`\nStatus: ${result.status}`));
          console.log(chalk.gray('DNS records can take up to 48 hours to propagate.'));
        }
      } catch (error: any) {
        spinner.fail(chalk.red('Verification check failed'));
        if (error.response) {
          console.error(chalk.red(`Error: ${error.response.data.detail || error.message}`));
        } else {
          console.error(chalk.red(`Error: ${error.message}`));
        }
        process.exit(1);
      }
    });

  return verify;
}
