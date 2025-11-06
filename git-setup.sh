#!/usr/bin/env bash
# BrainSAIT AI Automation - Git Setup and Push Script

set -e

echo "🚀 BrainSAIT AI Automation - Git Repository Setup"
echo "=================================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✓ Git repository initialized"
    echo ""
fi

# Check git configuration
if ! git config user.name > /dev/null 2>&1; then
    echo "⚙️  Git user not configured. Please configure:"
    echo ""
    read -p "Enter your name: " GIT_NAME
    read -p "Enter your email: " GIT_EMAIL
    git config user.name "$GIT_NAME"
    git config user.email "$GIT_EMAIL"
    echo "✓ Git user configured"
    echo ""
fi

# Check current status
echo "📊 Current git status:"
git status --short
echo ""

# Stage all files if there are changes
if [[ -n $(git status --porcelain) ]]; then
    echo "📝 Staging changes..."
    git add .
    echo "✓ All files staged"
    echo ""
    
    # Create commit
    read -p "Enter commit message (or press Enter for default): " COMMIT_MSG
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="Update: BrainSAIT AI automation enhancements"
    fi
    
    git commit -m "$COMMIT_MSG"
    echo "✓ Commit created"
    echo ""
fi

# Check for existing remote
if git remote get-url origin > /dev/null 2>&1; then
    EXISTING_REMOTE=$(git remote get-url origin)
    echo "⚠️  Remote 'origin' already exists: $EXISTING_REMOTE"
    read -p "Do you want to replace it? (y/N): " REPLACE_REMOTE
    if [[ $REPLACE_REMOTE =~ ^[Yy]$ ]]; then
        git remote remove origin
        echo "✓ Removed existing remote"
    else
        echo "Keeping existing remote. Ready to push!"
        echo ""
        echo "To push your code, run:"
        echo "  git push -u origin main"
        exit 0
    fi
fi

# Prompt for remote repository URL
echo "📡 Remote Repository Setup"
echo "=========================="
echo ""
echo "Please create a repository on GitHub/GitLab/Bitbucket first, then enter the URL."
echo "Examples:"
echo "  - GitHub: https://github.com/username/brainsait-ai-automation.git"
echo "  - GitLab: https://gitlab.com/username/brainsait-ai-automation.git"
echo "  - SSH: git@github.com:username/brainsait-ai-automation.git"
echo ""
read -p "Enter remote repository URL: " REMOTE_URL

if [ -z "$REMOTE_URL" ]; then
    echo "❌ No URL provided. Exiting."
    exit 1
fi

# Add remote
echo ""
echo "🔗 Adding remote..."
git remote add origin "$REMOTE_URL"
echo "✓ Remote 'origin' added: $REMOTE_URL"
echo ""

# Get current branch name
CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    CURRENT_BRANCH="main"
    git checkout -b main
    echo "✓ Created and switched to 'main' branch"
fi

# Push to remote
echo "📤 Pushing to remote..."
echo ""
read -p "Push to '$CURRENT_BRANCH' branch? (Y/n): " DO_PUSH

if [[ ! $DO_PUSH =~ ^[Nn]$ ]]; then
    git push -u origin "$CURRENT_BRANCH"
    echo ""
    echo "✅ Successfully pushed to remote!"
    echo ""
    echo "🎉 Your repository is now available at:"
    echo "   $REMOTE_URL"
else
    echo ""
    echo "⏸️  Push skipped. When ready, run:"
    echo "   git push -u origin $CURRENT_BRANCH"
fi

echo ""
echo "📚 Quick Git Commands:"
echo "  git status          # Check current status"
echo "  git add .           # Stage all changes"
echo "  git commit -m '...' # Commit changes"
echo "  git push            # Push to remote"
echo "  git pull            # Pull from remote"
echo ""
