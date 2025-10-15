/**
 * Script to rename .js files to .mjs for ESM builds
 */

const fs = require('fs');
const path = require('path');

function renameFiles(dir) {
  const files = fs.readdirSync(dir);

  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      renameFiles(filePath);
    } else if (file.endsWith('.js')) {
      const newPath = filePath.replace(/\.js$/, '.mjs');
      fs.renameSync(filePath, newPath);
      console.log(`Renamed: ${filePath} -> ${newPath}`);
    }
  }
}

const esmDir = path.join(__dirname, '../dist/esm');
if (fs.existsSync(esmDir)) {
  renameFiles(esmDir);
  console.log('ESM files renamed successfully');
} else {
  console.log('ESM directory not found, skipping rename');
}
