#!/bin/bash

# 🚀 Deploy Python Vector API to Railway.app
# Prerequisites: brew install railway
# Usage: ./deploy-railway.sh

set -e

echo "🚀 Deploying Python Vector API to Railway.app"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Error: Railway CLI not found"
    echo "💡 Install: brew install railway"
    exit 1
fi

# Login to Railway
echo "🔐 Logging in to Railway..."
railway login

# Initialize project (if not already)
if [ ! -f railway.json ]; then
    echo ""
    echo "📦 Initializing Railway project..."
    railway init
fi

# Set environment variables
echo ""
echo "⚙️  Setting environment variables..."
echo "Please enter your configuration:"
echo ""

read -p "DATABASE_URL: " DATABASE_URL
read -p "SUPABASE_URL: " SUPABASE_URL
read -p "SUPABASE_ANON_KEY: " SUPABASE_ANON_KEY

railway variables set DATABASE_URL="$DATABASE_URL"
railway variables set PYTHON_API_KEY="vsk_aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5zA7bC9dE1fG3hI5jK7lM9"
railway variables set SUPABASE_URL="$SUPABASE_URL"
railway variables set SUPABASE_ANON_KEY="$SUPABASE_ANON_KEY"
railway variables set ENVIRONMENT="production"
railway variables set LOG_LEVEL="INFO"

echo ""
echo "✅ Environment variables set!"

# Deploy
echo ""
echo "🚀 Deploying to Railway..."
railway up

# Create public domain
echo ""
echo "🌐 Creating public domain..."
railway domain

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Run: railway logs"
echo "2. Get URL: railway status"
echo "3. Test: curl <YOUR_RAILWAY_URL>/health"
echo ""
echo "🎉 Your API is now live on Railway!"
