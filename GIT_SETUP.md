# Quick Git Setup Guide

## Option 1: Interactive Setup (Recommended)

Run the automated setup script:

```bash
./git-setup.sh
```

This script will:
1. Initialize git repository if needed
2. Configure git user (if not configured)
3. Stage and commit your changes
4. Prompt for remote repository URL
5. Add remote and push your code

## Option 2: Manual Setup

### Step 1: Create a GitHub Repository

1. Go to https://github.com/new
2. Repository name: `brainsait-ai-automation`
3. Description: "AI-powered business discovery and digital maturity analysis for Saudi market"
4. Choose Private or Public
5. Don't initialize with README (we already have one)
6. Click "Create repository"

### Step 2: Configure Git (if needed)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 3: Initialize and Commit

```bash
cd /Users/fadil369/Desktop/brainsait_ai_automation

# Initialize git (if not already done)
git init

# Stage all files
git add .

# Create initial commit
git commit -m "Initial commit: BrainSAIT AI-powered business discovery system"
```

### Step 4: Add Remote and Push

Replace `USERNAME` with your GitHub username:

```bash
# Add remote repository
git remote add origin https://github.com/USERNAME/brainsait-ai-automation.git

# Rename branch to main (if needed)
git branch -M main

# Push to remote
git push -u origin main
```

## Option 3: Use GitHub CLI

If you have GitHub CLI installed:

```bash
cd /Users/fadil369/Desktop/brainsait_ai_automation

# Create repository and push
gh repo create brainsait-ai-automation --private --source=. --push

# Or for public repository
gh repo create brainsait-ai-automation --public --source=. --push
```

## Verify Push

After pushing, verify your repository:

```bash
# Check remote URL
git remote -v

# View commit history
git log --oneline

# Check branch
git branch -a
```

## Common Git Commands

```bash
# Check status
git status

# Stage specific files
git add src/brainsait_ai/cli.py

# Commit with message
git commit -m "Add new feature"

# Push changes
git push

# Pull latest changes
git pull

# Create new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main

# View commit history
git log --oneline --graph
```

## Troubleshooting

### Authentication Issues

If using HTTPS and getting authentication errors:

1. Use Personal Access Token instead of password
2. Generate token at: https://github.com/settings/tokens
3. Or switch to SSH:

```bash
git remote set-url origin git@github.com:USERNAME/brainsait-ai-automation.git
```

### Large Files Warning

If git warns about large files:

```bash
# See which files are large
git ls-files | xargs ls -lh | sort -k5 -h -r | head -20

# Add to .gitignore if needed
echo "data/*.parquet" >> .gitignore
echo "results/*" >> .gitignore
git rm --cached -r data/
```

### Merge Conflicts

If you get merge conflicts after pull:

```bash
# See conflicting files
git status

# Edit files to resolve conflicts
# Then stage and commit
git add .
git commit -m "Resolve merge conflicts"
```

---

**Need help?** Run `./git-setup.sh` for interactive guidance!
