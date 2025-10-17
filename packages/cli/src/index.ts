#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import { createVerifyCommand } from './commands/verify';
import { createKeysCommand } from './commands/keys';
import { createIndexCommand } from './commands/index-gen';
import { createAuthCommand } from './commands/auth';

const program = new Command();

program
  .name('iaindex')
  .description('IAIndex CLI - Command line tool for managing AI Index attestations')
  .version('1.0.0');

// Add commands
program.addCommand(createAuthCommand());
program.addCommand(createVerifyCommand());
program.addCommand(createKeysCommand());
program.addCommand(createIndexCommand());

// Custom help
program.on('--help', () => {
  console.log('');
  console.log(chalk.cyan('Examples:'));
  console.log('  $ iaindex auth login');
  console.log('  $ iaindex verify init example.com');
  console.log('  $ iaindex verify check <token>');
  console.log('  $ iaindex generate-keys -o ./keys');
  console.log('  $ iaindex create-index --interactive');
  console.log('  $ iaindex create-index config.json -s ./keys/private.pem');
  console.log('');
  console.log(chalk.cyan('Documentation:'));
  console.log('  https://docs.iaindex.org');
  console.log('');
});

// Parse arguments
program.parse(process.argv);

// Show help if no command provided
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
