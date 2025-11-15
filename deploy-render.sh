#!/bin/bash

# 🚀 Deploy Python Vector API to Render.com
# Usage: ./deploy-render.sh

set -e

echo "🚀 Deploying Python Vector API to Render.com"
echo ""

# Check if git repository exists
if [ ! -d .git ]; then
    echo "❌ Error: Not a git repository"
    echo "💡 Run: git init"
    exit 1
fi

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo ""
    git status -s
    echo ""
    read -p "Do you want to commit these changes? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        read -p "Enter commit message: " commit_msg
        git commit -m "$commit_msg"
    fi
fi

# Check if remote exists
if ! git remote | grep -q origin; then
    echo "❌ Error: No 'origin' remote found"
    echo "💡 Run: git remote add origin <YOUR_GITHUB_REPO_URL>"
    exit 1
fi

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
git push origin main || git push origin master

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Go to https://render.com"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Connect your GitHub repository"
echo "4. Configure:"
echo "   - Name: fitrecipes-vector-api"
echo "   - Environment: Docker"
echo "   - Region: Singapore"
echo "   - Branch: main (or master)"
echo "   - Instance Type: Free"
echo ""
echo "5. Add Environment Variables:"
echo "   - DATABASE_URL=<your_supabase_url>"
echo "   - PYTHON_API_KEY=vsk_aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5zA7bC9dE1fG3hI5jK7lM9"
echo "   - SUPABASE_URL=<your_supabase_url>"
echo "   - SUPABASE_ANON_KEY=<your_supabase_key>"
echo ""
echo "6. Click 'Create Web Service'"
echo ""
echo "7. Wait 5-10 minutes for deployment"
echo ""
echo "8. Test your API:"
echo "   curl https://fitrecipes-vector-api.onrender.com/health"
echo ""
echo "🎉 Done! Your API will be live at: https://fitrecipes-vector-api.onrender.com"
