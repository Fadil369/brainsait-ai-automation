#!/bin/bash

# Skill Folders Ecosystem Deployment Script
# This script deploys the skill folders API to Cloudflare Workers

set -e  # Exit on error

echo "🚀 Starting Skill Folders Ecosystem Deployment"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for required tools
echo -e "${YELLOW}Checking required tools...${NC}"
command -v node >/dev/null 2>&1 || { echo -e "${RED}Node.js is required but not installed.${NC}"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo -e "${RED}npm is required but not installed.${NC}"; exit 1; }
command -v wrangler >/dev/null 2>&1 || { echo -e "${YELLOW}wrangler not found, installing...${NC}"; npm install -g wrangler; }

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}Node.js version 18 or higher is required. Current: $(node -v)${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js $(node -v)${NC}"

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
npm ci
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Run tests
echo -e "\n${YELLOW}Running tests...${NC}"
if npm test; then
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
    exit 1
fi

# Build project
echo -e "\n${YELLOW}Building project...${NC}"
npm run build
if [ -f "dist/index.js" ]; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}✗ Build failed - dist/index.js not found${NC}"
    exit 1
fi

# Check Cloudflare configuration
echo -e "\n${YELLOW}Checking Cloudflare configuration...${NC}"
if [ -f "wrangler.toml" ]; then
    echo -e "${GREEN}✓ wrangler.toml found${NC}"
    
    # Extract project name
    PROJECT_NAME=$(grep -E '^name =' wrangler.toml | head -1 | cut -d'"' -f2)
    if [ -n "$PROJECT_NAME" ]; then
        echo -e "${GREEN}✓ Project name: $PROJECT_NAME${NC}"
    else
        echo -e "${YELLOW}⚠ Could not extract project name from wrangler.toml${NC}"
    fi
else
    echo -e "${RED}✗ wrangler.toml not found${NC}"
    exit 1
fi

# Deploy to Cloudflare Workers
echo -e "\n${YELLOW}Deploying to Cloudflare Workers...${NC}"
echo -e "${YELLOW}This will deploy to:${NC}"
echo -e "  - Development: https://$PROJECT_NAME.<your-subdomain>.workers.dev"
echo -e "  - Production:  https://$PROJECT_NAME-prod.<your-subdomain>.workers.dev"

# Ask for confirmation
read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

# Run deployment
echo -e "\n${YELLOW}Starting deployment...${NC}"
if wrangler deploy; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    
    # Get deployment URL
    echo -e "\n${YELLOW}Getting deployment information...${NC}"
    DEPLOYMENT_INFO=$(wrangler deployments list 2>/dev/null | head -5 || true)
    if [ -n "$DEPLOYMENT_INFO" ]; then
        echo "$DEPLOYMENT_INFO"
    fi
    
    # Test the deployment
    echo -e "\n${YELLOW}Testing deployment...${NC}"
    echo "You can test your deployment with:"
    echo "  curl https://$PROJECT_NAME.<your-subdomain>.workers.dev"
    echo "  curl https://$PROJECT_NAME.<your-subdomain>.workers.dev/health"
    echo "  curl https://$PROJECT_NAME.<your-subdomain>.workers.dev/api/skills"
    
else
    echo -e "${RED}❌ Deployment failed${NC}"
    echo "Check the error messages above and ensure:"
    echo "1. You're logged in to Cloudflare: wrangler login"
    echo "2. You have the correct permissions"
    echo "3. Your wrangler.toml is properly configured"
    exit 1
fi

# CI/CD reminder
echo -e "\n${YELLOW}CI/CD Setup Reminder:${NC}"
echo "The GitHub Actions workflow is configured at:"
echo "  .github/workflows/deploy-cloudflare.yml"
echo ""
echo "To enable automatic deployments:"
echo "1. Add secrets to your GitHub repository:"
echo "   - CLOUDFLARE_API_TOKEN"
echo "   - CLOUDFLARE_ACCOUNT_ID"
echo "2. Push to main/master branch to trigger deployment"

# Final message
echo -e "\n${GREEN}=============================================${NC}"
echo -e "${GREEN}🎉 Skill Folders Ecosystem Deployment Complete!${NC}"
echo -e "${GREEN}=============================================${NC}"
echo ""
echo "Your skill folders API is now deployed to Cloudflare Workers."
echo "The ecosystem includes:"
echo "  • Legal Auditor Compliance skills"
echo "  • Cyber Guardian MDR skills"
echo "  • Healthcare Insurance (Saudi Market) skills"
echo "  • Bilingual Arabic/English support"
echo ""
echo "Next steps:"
echo "1. Integrate with your AI agent platform"
echo "2. Configure authentication if needed"
echo "3. Monitor performance in Cloudflare dashboard"
echo "4. Add more skills as needed"
