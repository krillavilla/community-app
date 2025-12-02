#!/bin/bash

# Garden MVP - Quick Deploy Script
# Run this to deploy the simplified MVP for user testing

set -e  # Exit on error

echo "🌱 Garden MVP Deployment Starting..."
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found"
    echo "Please run this script from the community-app directory"
    exit 1
fi

# Step 1: Stop existing services
echo "📦 Stopping existing services..."
docker compose down

# Step 2: Run database migration
echo "🗄️  Running database migration (creating MVP tables)..."
docker compose run --rm backend alembic upgrade head

# Step 3: Start services
echo "🚀 Starting services..."
docker compose up -d

# Step 4: Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Step 5: Check health
echo "🏥 Checking service health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend might not be ready yet (this is normal, give it a minute)"
fi

# Step 6: Show next steps
echo ""
echo "✅ MVP Deployment Complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Next Steps:"
echo ""
echo "1. Test the API:"
echo "   http://localhost:8000/docs"
echo ""
echo "2. (Optional) Configure R2 storage for video uploads:"
echo "   - Edit backend/.env"
echo "   - Add R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ENDPOINT_URL"
echo "   - Restart: docker compose restart backend"
echo ""
echo "3. Setup nightly expiration worker:"
echo "   crontab -e"
echo "   # Add: 0 3 * * * cd $(pwd) && docker compose run --rm backend python -m app.workers.expiration_worker >> /tmp/garden-expiration.log 2>&1"
echo ""
echo "4. Update frontend to use MVP API"
echo "   - See MVP_DEPLOYMENT_GUIDE.md for code templates"
echo ""
echo "5. Test with real users!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Documentation:"
echo "   - MVP_DEPLOYMENT_GUIDE.md - Full deployment guide"
echo "   - MVP_SUMMARY.md - What was built"
echo ""
echo "🐛 Troubleshooting:"
echo "   docker compose logs backend"
echo "   docker compose logs frontend"
echo ""
echo "Good luck! 🌱 → 🚀"
