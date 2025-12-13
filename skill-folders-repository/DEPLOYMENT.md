# BrainSAIT Skills API - Deployment Guide

## Overview

This guide covers deploying the BrainSAIT Skills API to Cloudflare Workers with automated CI/CD through GitHub Actions.

## Prerequisites

- GitHub account with repository access
- Cloudflare account
- Node.js 18+ installed locally (for development)
- Basic understanding of Git and CI/CD

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Repository                     │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Push to main/master branch                       │ │
│  └───────────────┬────────────────────────────────────┘ │
│                  │                                        │
│                  ▼                                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │         GitHub Actions Workflow                    │ │
│  │  1. Install dependencies                           │ │
│  │  2. Run tests                                      │ │
│  │  3. Security audit                                 │ │
│  │  4. Lint code                                      │ │
│  │  5. Build project                                  │ │
│  │  6. Deploy to Cloudflare                           │ │
│  │  7. Run integration tests                          │ │
│  │  8. Verify deployment                              │ │
│  └───────────────┬────────────────────────────────────┘ │
└──────────────────┼──────────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────┐
    │      Cloudflare Workers (Global Edge)    │
    │  - Skill Folders API                     │
    │  - KV Storage (Skills Data)              │
    │  - Analytics                             │
    └──────────────────────────────────────────┘
```

## Cloudflare Setup

### Step 1: Create Cloudflare Account & Get Credentials

1. **Sign up** at [cloudflare.com](https://cloudflare.com) if you don't have an account
2. **Get Account ID**:
   - Go to Workers & Pages dashboard
   - Copy your Account ID from the right sidebar

3. **Create API Token**:
   - Go to My Profile → API Tokens
   - Click "Create Token"
   - Use "Edit Cloudflare Workers" template
   - Or create custom token with these permissions:
     - Account → Workers Scripts → Edit
     - Account → Workers KV Storage → Edit
   - Copy the token immediately (shown only once!)

### Step 2: Create KV Namespace

```bash
# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Create KV namespace for production
wrangler kv:namespace create "SKILLS_KV"

# Output will show:
# Add the following to your wrangler.toml:
# [[kv_namespaces]]
# binding = "SKILLS_KV"
# id = "your-kv-id-here"
```

Copy the KV namespace ID - you'll need it for `wrangler.toml`.

## GitHub Repository Setup

### Step 1: Add GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

1. **CLOUDFLARE_API_TOKEN**
   - Value: Your Cloudflare API token from above
   - Used for: Authenticating deployments

2. **CLOUDFLARE_ACCOUNT_ID**
   - Value: Your Cloudflare Account ID
   - Used for: Identifying your Cloudflare account

### Step 2: Configure wrangler.toml

Ensure your `skill-folders-repository/wrangler.toml` is configured:

```toml
name = "skill-folders-api"
account_id = "your-account-id-here"
compatibility_date = "2025-12-12"
compatibility_flags = ["nodejs_compat"]
main = "dist/index.js"
workers_dev = true

[env.production]
name = "skill-folders-api-prod"

[vars]
API_VERSION = "1.0.0"
ENVIRONMENT = "production"

[[kv_namespaces]]
binding = "SKILLS_KV"
id = "your-kv-namespace-id-here"

[build]
command = "npm run build"

[observability]
enabled = true
```

> Tip: Run `npm run build` first, then `npx wrangler versions upload` from the repository root. The root `wrangler.jsonc` mirrors this configuration, uses `skill-folders-repository/dist/index.js` as the entry point, and avoids missing entry-point errors. The account ID is sourced from your authenticated Wrangler context or CLI arguments, so it is not duplicated in the root config.

**Important**: Replace `your-account-id-here` and `your-kv-namespace-id-here` with your actual values.

## CI/CD Pipeline

The deployment workflow (`.github/workflows/deploy-cloudflare.yml`) automatically runs on:
- Push to `main` or `master` branch
- Pull requests to `main` or `master` branch
- Manual trigger via `workflow_dispatch`

### Workflow Steps:

1. **Checkout repository**: Gets latest code
2. **Setup Node.js**: Installs Node 18
3. **Install dependencies**: Runs `npm ci` for clean install
4. **Run tests**: Executes test suite
5. **Security audit**: Checks for vulnerabilities
6. **Lint code**: Checks code quality
7. **Build project**: Creates production bundle
8. **Deploy to Cloudflare**: Pushes to Workers
9. **Integration tests**: Tests live endpoints
10. **Verify deployment**: Health check on deployed API

## Local Development

### Setup

```bash
# Clone repository
git clone https://github.com/Fadil369/brainsait-ai-automation.git
cd brainsait-ai-automation/skill-folders-repository

# Install dependencies
npm install

# Create .env file (optional, for local testing)
cp .env.example .env
```

### Development Commands

```bash
# Start local dev server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Run linter
npm run lint

# Format code
npm run format
```

### Testing Locally

```bash
# Start dev server
npm run dev
# API available at http://localhost:8787

# In another terminal, test endpoints:
curl http://localhost:8787/health
curl http://localhost:8787/api/pricing

# Test with API key
curl -H "Authorization: Bearer sk_test123" \
  http://localhost:8787/api/skills
```

## Manual Deployment

If you need to deploy manually (without CI/CD):

```bash
cd skill-folders-repository

# Login to Cloudflare
wrangler login

# Deploy to production
wrangler deploy --env production

# Or deploy to dev
wrangler deploy
```

## Deployment Verification

After deployment, verify the API is working:

```bash
# Check health endpoint
curl https://skill-folders-api.brainsait-fadil.workers.dev/health

# Expected response:
# {"status":"ok","environment":"cloudflare-workers","timestamp":"..."}

# Check service info
curl https://skill-folders-api.brainsait-fadil.workers.dev/

# Test authenticated endpoint (replace with real API key)
curl -H "Authorization: Bearer sk_test123" \
  https://skill-folders-api.brainsait-fadil.workers.dev/api/skills
```

## Monitoring & Logs

### View Logs

```bash
# Stream logs in real-time
wrangler tail

# Filter logs
wrangler tail --status ok
wrangler tail --status error
```

### Cloudflare Dashboard

Monitor your Worker in the Cloudflare dashboard:
1. Go to Workers & Pages
2. Click on your worker (`skill-folders-api`)
3. View:
   - Request metrics
   - Error rate
   - CPU time
   - Bandwidth usage

### Analytics

Enable analytics in `wrangler.toml`:

```toml
[observability]
enabled = true

[[analytics_engine_datasets]]
binding = "ANALYTICS"
dataset = "skills_analytics"
```

## Environment-Specific Configuration

### Development Environment

```toml
# Automatic for wrangler dev
name = "skill-folders-api-dev"
workers_dev = true
```

### Production Environment

```toml
[env.production]
name = "skill-folders-api-prod"
routes = [
  { pattern = "api.brainsait.com/*", zone_name = "brainsait.com" }
]
```

## Custom Domain Setup

To use a custom domain (e.g., `api.brainsait.com`):

1. **Add domain to Cloudflare**:
   - Add your domain to Cloudflare
   - Update nameservers at your registrar

2. **Create DNS record**:
   - Type: AAAA
   - Name: api
   - Content: 100:: (Cloudflare Workers placeholder)
   - Proxy status: Proxied

3. **Add route in wrangler.toml**:
   ```toml
   [env.production]
   routes = [
     { pattern = "api.brainsait.com/*", zone_name = "brainsait.com" }
   ]
   ```

4. **Deploy**:
   ```bash
   wrangler deploy --env production
   ```

## Rollback Procedure

If a deployment causes issues:

### Option 1: Rollback via Cloudflare Dashboard

1. Go to Workers & Pages → Your Worker
2. Click "Deployments" tab
3. Find previous working version
4. Click "Rollback to this deployment"

### Option 2: Rollback via Git

```bash
# Find previous working commit
git log --oneline

# Revert to previous commit
git revert <commit-hash>
git push origin main

# CI/CD will automatically deploy the reverted version
```

### Option 3: Emergency Manual Deployment

```bash
# Checkout previous working commit
git checkout <commit-hash>

# Deploy manually
cd skill-folders-repository
wrangler deploy --env production

# Return to main branch
git checkout main
```

## Security Best Practices

1. **Secrets Management**:
   - Never commit API tokens to Git
   - Use GitHub Secrets for CI/CD
   - Rotate API tokens every 90 days

2. **API Key Protection**:
   - Generate strong API keys (`sk_` prefix + 32 random chars)
   - Store in KV with encryption at rest
   - Implement rate limiting

3. **Dependency Security**:
   - Run `npm audit` regularly
   - Update dependencies monthly
   - Monitor GitHub Dependabot alerts

4. **CORS Configuration**:
   - Restrict origins in production
   - Use specific allowed headers
   - Implement CSRF protection for state-changing operations

## Troubleshooting

### Common Issues

#### 1. Build Fails

```bash
# Check Node version
node --version  # Should be 18+

# Clean install
rm -rf node_modules package-lock.json
npm install

# Try build again
npm run build
```

#### 2. Deployment Fails - Authentication Error

- Verify `CLOUDFLARE_API_TOKEN` is set correctly in GitHub Secrets
- Ensure token has correct permissions (Workers Scripts → Edit)
- Check token hasn't expired

#### 3. Worker Doesn't Respond

```bash
# Check if worker exists
wrangler list

# View worker logs
wrangler tail

# Check routes
wrangler routes list
```

#### 4. KV Namespace Not Found

```bash
# List KV namespaces
wrangler kv:namespace list

# Create if missing
wrangler kv:namespace create "SKILLS_KV"

# Update wrangler.toml with new ID
```

## Performance Optimization

1. **Bundle Size**:
   - Current: ~64 KB (excellent)
   - Target: < 100 KB
   - Use tree-shaking and code splitting

2. **Cold Start**:
   - Cloudflare Workers: <10ms
   - Optimize imports
   - Avoid heavy dependencies

3. **Response Time**:
   - Target: < 100ms for API calls
   - Use KV for caching
   - Implement edge caching

## Cost Optimization

### Free Tier Limits (Cloudflare Workers)

- 100,000 requests/day
- 10ms CPU time per request
- Unlimited bandwidth (egress)

### Paid Plan ($5/month)

- 10 million requests/month included
- $0.50 per additional million
- Higher CPU time limits

### Cost Monitoring

```bash
# View usage in dashboard
# Workers & Pages → Analytics

# Estimate monthly cost
# (Daily requests × 30) / 1,000,000 × $0.50
```

## Support & Resources

- **Documentation**: [workers.cloudflare.com](https://workers.cloudflare.com)
- **Community**: [community.cloudflare.com](https://community.cloudflare.com)
- **Status**: [cloudflarestatus.com](https://cloudflarestatus.com)
- **Support**: Open GitHub issue or contact sales@brainsait.com

## Next Steps

1. ✅ Complete Cloudflare setup
2. ✅ Configure GitHub secrets
3. ✅ Push to main branch (triggers deployment)
4. ✅ Verify deployment
5. ⬜ Set up custom domain (optional)
6. ⬜ Configure monitoring alerts
7. ⬜ Implement advanced features (webhooks, analytics)

---

**Deployment Version**: 1.0.0  
**Last Updated**: 2025-12-12  
**Maintainer**: BrainSAIT DevOps Team
