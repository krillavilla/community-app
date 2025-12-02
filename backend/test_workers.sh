#!/bin/bash
# Test script to run Garden System workers manually

echo "==================================="
echo "Testing Garden System Workers"
echo "==================================="

echo ""
echo "1. Running Lifecycle Worker..."
docker compose run --rm backend python -m app.workers.lifecycle_worker

echo ""
echo "2. Running Climate Worker..."
docker compose run --rm backend python -m app.workers.climate_worker

echo ""
echo "3. Running Compost Worker..."
docker compose run --rm backend python -m app.workers.compost_worker

echo ""
echo "==================================="
echo "All workers completed!"
echo "==================================="
