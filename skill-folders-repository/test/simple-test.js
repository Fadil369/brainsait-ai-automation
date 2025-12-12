// Simple test to verify the skill folders structure
const fs = require('fs');
const path = require('path');

console.log('Testing Skill Folders Structure...\n');

// Check main directories
const requiredDirs = [
  '01-legal-auditor-compliance',
  '02-cyber-guardian-mdr', 
  '03-researcher-automation',
  '04-healthcare-insurance-saudi'
];

const basePath = __dirname + '/../';
let allTestsPassed = true;

// Test 1: Check main directories exist
console.log('Test 1: Checking main skill directories...');
requiredDirs.forEach(dir => {
  const dirPath = path.join(basePath, dir);
  if (fs.existsSync(dirPath)) {
    console.log(`  ✓ ${dir} exists`);
  } else {
    console.log(`  ✗ ${dir} missing`);
    allTestsPassed = false;
  }
});

// Test 2: Check README files
console.log('\nTest 2: Checking README files...');
const readmeFiles = [
  'README.md',
  '01-legal-auditor-compliance/README.md',
  '02-cyber-guardian-mdr/README.md'
];

readmeFiles.forEach(file => {
  const filePath = path.join(basePath, file);
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    if (content.length > 100) {
      console.log(`  ✓ ${file} exists with sufficient content (${content.length} chars)`);
    } else {
      console.log(`  ⚠ ${file} exists but content may be insufficient (${content.length} chars)`);
    }
  } else {
    console.log(`  ✗ ${file} missing`);
    allTestsPassed = false;
  }
});

// Test 3: Check SKILL.md files
console.log('\nTest 3: Checking SKILL.md files...');
const skillFiles = [
  '01-legal-auditor-compliance/01-regulatory-knowledge-base/SKILL.md'
];

skillFiles.forEach(file => {
  const filePath = path.join(basePath, file);
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    if (content.includes('SKILL') && content.includes('Description')) {
      console.log(`  ✓ ${file} exists with proper structure`);
    } else {
      console.log(`  ⚠ ${file} exists but may not have proper structure`);
    }
  } else {
    console.log(`  ✗ ${file} missing`);
    allTestsPassed = false;
  }
});

// Test 4: Check Cloudflare configuration
console.log('\nTest 4: Checking Cloudflare configuration...');
const cfFiles = [
  'wrangler.toml',
  'package.json',
  'src/index.js'
];

cfFiles.forEach(file => {
  const filePath = path.join(basePath, file);
  if (fs.existsSync(filePath)) {
    console.log(`  ✓ ${file} exists`);
    
    // Check specific content for key files
    if (file === 'wrangler.toml') {
      const content = fs.readFileSync(filePath, 'utf8');
      if (content.includes('skill-folders-api')) {
        console.log(`    → Contains skill-folders-api configuration`);
      }
    }
    
    if (file === 'package.json') {
      const content = fs.readFileSync(filePath, 'utf8');
      const pkg = JSON.parse(content);
      if (pkg.name === 'skill-folders-api') {
        console.log(`    → Package name: ${pkg.name}`);
      }
    }
  } else {
    console.log(`  ✗ ${file} missing`);
    allTestsPassed = false;
  }
});

// Test 5: Check CI/CD configuration
console.log('\nTest 5: Checking CI/CD configuration...');
const ciPath = path.join(basePath, '../../.github/workflows/deploy-cloudflare.yml');
if (fs.existsSync(ciPath)) {
  const content = fs.readFileSync(ciPath, 'utf8');
  if (content.includes('Cloudflare Workers') && content.includes('wrangler-action')) {
    console.log(`  ✓ CI/CD workflow exists and configured for Cloudflare`);
  } else {
    console.log(`  ⚠ CI/CD workflow exists but may not be properly configured`);
  }
} else {
  console.log(`  ⚠ CI/CD workflow not found in expected location`);
}

// Summary
console.log('\n' + '='.repeat(50));
if (allTestsPassed) {
  console.log('✅ All critical tests passed!');
  console.log('The skill folders ecosystem is ready for deployment.');
} else {
  console.log('⚠ Some tests failed. Review the output above.');
}

console.log('\nNext steps:');
console.log('1. Install dependencies: cd skill-folders-repository && npm install');
console.log('2. Test locally: npm run dev');
console.log('3. Deploy to Cloudflare: npm run deploy');
console.log('4. Verify deployment with: curl https://skill-folders-api.YOUR_SUBDOMAIN.workers.dev');
