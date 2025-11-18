#!/bin/bash

# Quick start script for Garden platform
# Sets up and runs the entire platform

set -e

echo "======================================"
echo "Garden Platform - Quick Start"
echo "======================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker is installed"
echo "✓ Docker Compose is installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please configure .env file with your Auth0 credentials"
    echo "   Then run this script again."
    exit 0
fi

# Check if frontend/.env exists
if [ ! -f frontend/.env ]; then
    echo "Creating frontend/.env file from template..."
    cp frontend/.env.example frontend/.env
    echo "⚠️  Please configure frontend/.env file with your Auth0 credentials"
    echo "   Then run this script again."
    exit 0
fi

echo "Building Docker images..."
docker compose build

echo ""
echo "Starting services..."
docker compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Wait for database
echo "Waiting for database..."
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U garden > /dev/null 2>&1; then
        echo "✓ Database is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Database failed to start"
        exit 1
    fi
    sleep 2
done

# Run migrations
echo ""
echo "Running database migrations..."
docker compose exec -T backend alembic upgrade head

# Seed database
echo ""
echo "Seeding database with initial data..."
docker compose exec -T backend python seed_data.py

echo ""
echo "======================================"
echo "✓ Garden Platform is ready!"
echo "======================================"
echo ""
echo "Access your application:"
echo "  🌐 Frontend:    http://localhost"
echo "  🔧 Backend:     http://localhost:8000"
echo "  📚 API Docs:    http://localhost:8000/docs"
echo "  🤖 ML Service:  http://localhost:8001"
echo "  📊 ML Docs:     http://localhost:8001/docs"
echo ""
echo "Next steps:"
echo "  1. Configure Auth0 application (see README.md)"
echo "  2. Update .env and frontend/.env with Auth0 credentials"
echo "  3. Visit http://localhost to start using Garden!"
echo ""
echo "Useful commands:"
echo "  make logs      - View logs"
echo "  make down      - Stop services"
echo "  make restart   - Restart services"
echo ""
