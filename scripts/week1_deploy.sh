#!/bin/bash
# Week 1 Foundation Deployment Script
# Run this after completing onboarding setup

set -e  # Exit on error

echo "🌱 Garden Platform - Week 1 Foundation Setup"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: Must be run from project root directory"
    exit 1
fi

# Step 1: Rebuild backend with new code
echo "📦 Step 1: Rebuilding backend container..."
docker compose down backend
docker compose build --no-cache backend

# Step 2: Run database migrations
echo "🗄️  Step 2: Running database migrations..."
docker compose up -d postgres
sleep 5  # Wait for postgres to be ready

# Run migration
docker compose run --rm backend alembic upgrade head

# Step 3: Rebuild and restart all services
echo "🚀 Step 3: Restarting all services..."
docker compose up -d

# Step 4: Wait for services to be ready
echo "⏳ Step 4: Waiting for services to start..."
sleep 10

# Step 5: Test GDPR endpoints
echo "🧪 Step 5: Testing new endpoints..."
echo ""
echo "Testing health check..."
curl -s http://localhost:8000/health | jq '.'

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to http://localhost and complete onboarding"
echo "2. Test GDPR export: GET /api/v1/gdpr/export"
echo "3. Test age verification: POST /api/v1/users/me/verify-age"
echo ""
echo "📖 View API docs: http://localhost:8000/docs"
echo ""
