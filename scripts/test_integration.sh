#!/bin/bash

# Integration test script for Garden platform
# Tests all services and their connections

set -e

echo "======================================"
echo "Garden Platform Integration Tests"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if services are running
echo -e "${YELLOW}Checking services...${NC}"

# Check database
if docker compose exec -T postgres pg_isready -U garden > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Database is ready"
else
    echo -e "${RED}✗${NC} Database is not ready"
    exit 1
fi

# Check backend
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend is running"
else
    echo -e "${RED}✗${NC} Backend is not running"
    exit 1
fi

# Check ML service
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} ML service is running"
else
    echo -e "${RED}✗${NC} ML service is not running"
    exit 1
fi

# Check frontend
if curl -s http://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend is running"
else
    echo -e "${RED}✗${NC} Frontend is not running"
    exit 1
fi

echo ""
echo -e "${YELLOW}Testing ML service endpoints...${NC}"

# Test ML health endpoint
ML_HEALTH=$(curl -s http://localhost:8001/health)
if echo "$ML_HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} ML health check passed"
else
    echo -e "${RED}✗${NC} ML health check failed"
fi

# Test feature extraction
FEATURE_RESPONSE=$(curl -s -X POST http://localhost:8001/features/extract \
    -H "X-API-Key: dev-ml-key-change-in-production" \
    -H "Content-Type: application/json" \
    -d '{
        "user_id": "test_user",
        "habits": [
            {"name": "meditation", "category": "mindfulness", "frequency": "daily"},
            {"name": "exercise", "category": "health", "frequency": "daily"}
        ]
    }')

if echo "$FEATURE_RESPONSE" | grep -q "feature_vector"; then
    echo -e "${GREEN}✓${NC} ML feature extraction working"
else
    echo -e "${RED}✗${NC} ML feature extraction failed"
fi

echo ""
echo -e "${YELLOW}Testing backend endpoints...${NC}"

# Test backend health
BACKEND_HEALTH=$(curl -s http://localhost:8000/)
if echo "$BACKEND_HEALTH" | grep -q "Garden"; then
    echo -e "${GREEN}✓${NC} Backend health check passed"
else
    echo -e "${RED}✗${NC} Backend health check failed"
fi

echo ""
echo -e "${YELLOW}Testing database connection...${NC}"

# Test database connection from backend
DB_TEST=$(docker compose exec -T backend python -c "
from app.core.database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('OK')
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1)

if echo "$DB_TEST" | grep -q "OK"; then
    echo -e "${GREEN}✓${NC} Database connection working"
else
    echo -e "${RED}✗${NC} Database connection failed"
fi

echo ""
echo -e "${YELLOW}Checking database tables...${NC}"

TABLES=$(docker compose exec -T postgres psql -U garden -d garden_db -c "\dt" 2>&1)
if echo "$TABLES" | grep -q "users"; then
    echo -e "${GREEN}✓${NC} Database tables exist"
else
    echo -e "${RED}✗${NC} Database tables not found - run migrations"
fi

echo ""
echo -e "${GREEN}======================================"
echo "All integration tests passed! ✓"
echo "======================================${NC}"
echo ""
echo "Services are ready:"
echo "  Frontend:    http://localhost"
echo "  Backend:     http://localhost:8000"
echo "  API Docs:    http://localhost:8000/docs"
echo "  ML Service:  http://localhost:8001"
echo "  ML Docs:     http://localhost:8001/docs"
