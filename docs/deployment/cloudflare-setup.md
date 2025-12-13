# Cloudflare Workers Setup & Deployment Guide

## 🚀 Overview

This guide covers the complete setup process for deploying the BrainSAIT Skills API to Cloudflare Workers, including security best practices, environment configuration, and CI/CD integration.

---

## 📋 Prerequisites

- Cloudflare account (Free tier or above)
- Node.js 18+ installed
- Git configured
- Access to GitHub repository settings (for CI/CD)

---

## 🔐 Security Best Practices

**IMPORTANT**: Never commit sensitive credentials to version control. All secrets must be managed through:
- Environment variables (local development)
- GitHub Secrets (CI/CD)
- Cloudflare environment variables (runtime)

Refer to [SECURITY.md](../../SECURITY.md) for comprehensive security guidelines.

---

## 1️⃣ Cloudflare Account Setup

### Create/Access Your Cloudflare Account

1. Go to https://dash.cloudflare.com/sign-up
2. Complete registration or sign in
3. Navigate to **Workers & Pages** in the left sidebar

### Obtain Your Account ID

1. In Cloudflare Dashboard, go to **Workers & Pages**
2. Click on **Overview** tab
3. Your Account ID is displayed on the right side
4. Copy this ID - you'll need it for environment configuration

**📝 Note**: While Cloudflare account IDs are not considered highly sensitive and are often visible in public configurations, using environment variables for them provides consistency in configuration management and makes it easier to manage multiple environments.

---

## 2️⃣ API Token Creation

### Generate Worker API Token

1. Go to **My Profile** → **API Tokens** (https://dash.cloudflare.com/profile/api-tokens)
2. Click **Create Token**
3. Use the **Edit Cloudflare Workers** template
4. Configure permissions:
   - **Account** → **Cloudflare Workers Scripts** → **Edit**
   - **Account** → **Workers KV Storage** → **Edit**
   - **Zone** → **Workers Routes** → **Edit** (if using custom domains)
5. Set **Account Resources**:
   - Include → Specific account → [Your Account]
6. Set **Client IP Address Filtering** (optional but recommended):
   - Add your development machine IP
   - Add GitHub Actions IP ranges for CI/CD
7. Set **TTL**: Recommended 1 year or less
8. Click **Continue to summary** → **Create Token**
9. **IMPORTANT**: Copy the token immediately - it won't be shown again

### Token Scopes Required

Minimum required permissions:
```
Account:
  - Workers Scripts: Edit
  - Workers KV Storage: Edit
  
Zone (if using custom domains):
  - Workers Routes: Edit
```

---

## 3️⃣ KV Namespace Provisioning

KV namespaces store persistent data for your Workers. You need separate namespaces for each environment.

### Create Namespaces via Wrangler CLI

```bash
# Install wrangler globally (if not already installed)
npm install -g wrangler

# Authenticate with Cloudflare
wrangler login

# Create development namespace
wrangler kv:namespace create "SKILLS_KV" --preview

# Create production namespace
wrangler kv:namespace create "SKILLS_KV"

# Create staging namespace (optional)
wrangler kv:namespace create "SKILLS_KV_STAGING"
```

### Create Namespaces via Dashboard

1. Go to **Workers & Pages** → **KV**
2. Click **Create namespace**
3. Name it: `skills-kv-dev`, `skills-kv-staging`, `skills-kv-prod`
4. Copy the namespace IDs for each environment

### Note the Namespace IDs

After creation, note the namespace IDs:
```
Development: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Staging:     yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
Production:  zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
```

---

## 4️⃣ Local Development Setup

### Clone Repository

```bash
git clone https://github.com/Fadil369/brainsait-ai-automation.git
cd brainsait-ai-automation/skill-folders-repository
```

### Create Environment File

```bash
# Copy the example environment file
cp ../.env.example ../.env

# Edit the .env file with your values
nano ../.env
```

### Configure .env File

```bash
# Cloudflare Workers Configuration
CLOUDFLARE_ACCOUNT_ID=your-actual-account-id-here
CLOUDFLARE_API_TOKEN=your-actual-api-token-here

# KV Namespace IDs
KV_NAMESPACE_ID_DEV=your-dev-kv-namespace-id
KV_NAMESPACE_ID_STAGING=your-staging-kv-namespace-id
KV_NAMESPACE_ID_PROD=your-prod-kv-namespace-id

# Environment
ENVIRONMENT=development
API_VERSION=1.0.0
```

### Verify Configuration

The `wrangler.toml` file is configured to automatically use the `CLOUDFLARE_ACCOUNT_ID` environment variable:

```toml
name = "skill-folders-api"
# account_id is loaded from CLOUDFLARE_ACCOUNT_ID environment variable
# Set via GitHub Secrets or local .env file
compatibility_date = "2025-12-12"
```

Wrangler will automatically read the `CLOUDFLARE_ACCOUNT_ID` from your environment.

### Install Dependencies

```bash
npm install
```

### Test Local Development

```bash
# Run in development mode
npm run dev

# In another terminal, test the endpoint
curl http://localhost:8787/health
```

---

## 5️⃣ GitHub Secrets Configuration

For CI/CD pipelines, configure GitHub Secrets to securely store credentials.

### Add Secrets to GitHub

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `CLOUDFLARE_ACCOUNT_ID` | Your Account ID | Cloudflare account identifier |
| `CLOUDFLARE_API_TOKEN` | Your API Token | Token with Workers edit permissions |

### Verify Workflow Configuration

The GitHub Actions workflow (`.github/workflows/deploy-cloudflare.yml`) is pre-configured to use these secrets:

```yaml
- name: Deploy to Cloudflare Workers
  uses: cloudflare/wrangler-action@v3
  with:
    apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
    accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
    command: deploy
    workingDirectory: 'skill-folders-repository'
```

---

## 6️⃣ Environment-Specific Deployments

### Development Environment

```bash
# Deploy to development
npm run deploy
```

### Production Environment

```bash
# Deploy to production
wrangler deploy --env production
```

### Custom Environment Variables

To pass additional environment variables during deployment:

```bash
# Using wrangler
wrangler deploy --env production --var API_VERSION:2.0.0

# Or configure in wrangler.toml
[env.production]
name = "skill-folders-api-prod"

[vars.ENV.production]
API_VERSION = "2.0.0"
ENVIRONMENT = "production"
```

---

## 7️⃣ Testing Deployment

### Health Check

```bash
# Development
curl https://skill-folders-api.brainsait-fadil.workers.dev/health

# Production
curl https://skill-folders-api-prod.brainsait-fadil.workers.dev/health
```

### API Endpoints

```bash
# List skills
curl https://skill-folders-api.brainsait-fadil.workers.dev/api/skills

# Get specific skill
curl https://skill-folders-api.brainsait-fadil.workers.dev/api/skills/legal-compliance
```

---

## 8️⃣ Monitoring & Logs

### View Logs

```bash
# Tail logs in real-time
wrangler tail

# Filter by environment
wrangler tail --env production

# Filter by status
wrangler tail --status error
```

### Cloudflare Dashboard

1. Go to **Workers & Pages**
2. Click on your worker
3. View **Metrics**, **Analytics**, and **Logs** tabs

---

## 9️⃣ Troubleshooting

### Common Issues

#### Authentication Error

```
Error: Authentication error
```

**Solution**: 
- Verify `CLOUDFLARE_API_TOKEN` is correct
- Check token permissions
- Ensure token hasn't expired

#### Account ID Not Found

```
Error: Account ID not found
```

**Solution**:
- Verify `CLOUDFLARE_ACCOUNT_ID` is set correctly
- Check that account ID matches your Cloudflare account

#### KV Namespace Error

```
Error: KV namespace binding not found
```

**Solution**:
- Verify KV namespace IDs in `wrangler.toml`
- Ensure namespaces are created in Cloudflare dashboard
- Check namespace permissions

#### Deployment Fails in CI/CD

**Solution**:
- Verify GitHub Secrets are configured correctly
- Check GitHub Actions workflow logs
- Ensure `package-lock.json` is committed

---

## 🔒 Security Checklist

Before going to production, verify:

- [ ] No hard-coded credentials in code or config files
- [ ] All secrets stored in GitHub Secrets or environment variables
- [ ] `.env` file is in `.gitignore`
- [ ] API token has minimal required permissions
- [ ] Token IP restrictions configured (if applicable)
- [ ] HTTPS/TLS enabled for all endpoints
- [ ] Rate limiting configured
- [ ] Error messages don't expose sensitive information
- [ ] Audit logging enabled
- [ ] Regular security audits scheduled

---

## 📚 Additional Resources

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Wrangler CLI Reference](https://developers.cloudflare.com/workers/wrangler/)
- [KV Storage Guide](https://developers.cloudflare.com/workers/runtime-apis/kv/)
- [GitHub Actions with Cloudflare](https://github.com/cloudflare/wrangler-action)
- [BrainSAIT Security Policy](../../SECURITY.md)

---

## 🆘 Support

- **Documentation**: [Project README](../../README.md)
- **Issues**: [GitHub Issues](https://github.com/Fadil369/brainsait-ai-automation/issues)
- **Security**: See [SECURITY.md](../../SECURITY.md) for reporting vulnerabilities

---

**Last Updated**: 2025-12-13  
**Maintained by**: BrainSAIT Team
