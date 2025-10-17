import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import inquirer from 'inquirer';
import { createAPIClient } from '../api';
import { loadConfig, getConfigPath } from '../config';

export function createAuthCommand(): Command {
  const auth = new Command('auth');
  auth.description('Authentication commands');

  // Login command
  auth
    .command('login')
    .description('Login to IAIndex')
    .option('-e, --email <email>', 'Email address')
    .option('-p, --password <password>', 'Password')
    .action(async (options) => {
      let email = options.email;
      let password = options.password;

      // Prompt for credentials if not provided
      if (!email || !password) {
        const answers = await inquirer.prompt([
          {
            type: 'input',
            name: 'email',
            message: 'Email:',
            when: !email,
            validate: (input) => input.length > 0 || 'Email is required'
          },
          {
            type: 'password',
            name: 'password',
            message: 'Password:',
            when: !password,
            validate: (input) => input.length > 0 || 'Password is required'
          }
        ]);

        email = email || answers.email;
        password = password || answers.password;
      }

      const spinner = ora('Logging in...').start();

      try {
        const api = createAPIClient();
        const result = await api.login(email, password);

        spinner.succeed(chalk.green('Login successful!'));

        console.log('\n' + chalk.cyan('Credentials saved to:'));
        console.log(chalk.white(getConfigPath()));
        console.log('\n' + chalk.gray(`User ID: ${result.userId}`));
      } catch (error: any) {
        spinner.fail(chalk.red('Login failed'));
        if (error.response) {
          console.error(chalk.red(`Error: ${error.response.data.detail || error.message}`));
        } else {
          console.error(chalk.red(`Error: ${error.message}`));
        }
        process.exit(1);
      }
    });

  // Status command
  auth
    .command('status')
    .description('Check authentication status')
    .action(() => {
      const config = loadConfig();

      if (config.token) {
        console.log(chalk.green('✓ Authenticated'));
        console.log('\n' + chalk.cyan('Configuration:'));
        console.log(chalk.yellow('API URL:  ') + chalk.white(config.apiBaseUrl));
        console.log(chalk.yellow('User ID:  ') + chalk.white(config.userId || 'N/A'));
        console.log(chalk.yellow('Config:   ') + chalk.white(getConfigPath()));
      } else {
        console.log(chalk.yellow('Not authenticated'));
        console.log(chalk.gray('\nRun: iaindex auth login'));
      }
    });

  // Logout command
  auth
    .command('logout')
    .description('Logout from IAIndex')
    .action(() => {
      const config = loadConfig();

      if (config.token) {
        delete config.token;
        delete config.userId;

        const { saveConfig } = require('../config');
        saveConfig(config);

        console.log(chalk.green('✓ Logged out successfully'));
      } else {
        console.log(chalk.yellow('Not currently logged in'));
      }
    });

  return auth;
}
