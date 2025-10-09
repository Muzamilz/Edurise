#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🧹 Clearing TypeScript and build cache...');

// Directories to clean
const cacheDirs = [
  'node_modules/.vite',
  'node_modules/.cache',
  'dist',
  '.nuxt',
  '.output'
];

// Files to clean
const cacheFiles = [
  'tsconfig.tsbuildinfo'
];

// Clean directories
cacheDirs.forEach(dir => {
  const fullPath = path.join(__dirname, dir);
  if (fs.existsSync(fullPath)) {
    console.log(`Removing ${dir}...`);
    fs.rmSync(fullPath, { recursive: true, force: true });
  }
});

// Clean files
cacheFiles.forEach(file => {
  const fullPath = path.join(__dirname, file);
  if (fs.existsSync(fullPath)) {
    console.log(`Removing ${file}...`);
    fs.unlinkSync(fullPath);
  }
});

console.log('✅ Cache cleared successfully!');
console.log('💡 Run "npm run dev" to restart the development server.');