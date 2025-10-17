#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🔍 Verifying import structure...');

// Check for any remaining problematic imports
const problematicImports = [
  'useApi',
  'useTokens',
  'useAuthStore',
  'stores/',
  'composables/useApi'
];

function checkFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const issues = [];
    
    problematicImports.forEach(importPattern => {
      if (content.includes(importPattern)) {
        issues.push(`Found "${importPattern}" in ${filePath}`);
      }
    });
    
    return issues;
  } catch (error) {
    return [];
  }
}

function scanDirectory(dir, issues = []) {
  try {
    const files = fs.readdirSync(dir);
    
    files.forEach(file => {
      const fullPath = path.join(dir, file);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory() && !file.startsWith('.') && file !== 'node_modules') {
        scanDirectory(fullPath, issues);
      } else if (file.endsWith('.ts') || file.endsWith('.vue')) {
        const fileIssues = checkFile(fullPath);
        issues.push(...fileIssues);
      }
    });
  } catch (error) {
    // Directory doesn't exist or can't be read
  }
  
  return issues;
}

// Scan the src directory
const issues = scanDirectory(path.join(__dirname, 'src'));

if (issues.length === 0) {
  console.log('✅ All imports look good!');
  console.log('✅ No problematic import patterns found');
  console.log('✅ Ready to start development server');
} else {
  console.log('❌ Found import issues:');
  issues.forEach(issue => console.log(`  - ${issue}`));
}

// Check if key files exist
const keyFiles = [
  'src/services/api.ts',
  'src/services/auth.ts',
  'src/composables/useAuth.ts',
  'src/composables/useCourses.ts',
  'src/composables/useAdmin.ts',
  'src/main.ts'
];

console.log('\n📋 Key files check:');
keyFiles.forEach(file => {
  const fullPath = path.join(__dirname, file);
  if (fs.existsSync(fullPath)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file} - Missing!`);
  }
});

console.log('\n🚀 Next steps:');
console.log('1. Run: npm install (to update dependencies)');
console.log('2. Run: npm run dev (to start development server)');
console.log('3. Navigate to: http://localhost:3000');