"""
API v1 - Health endpoints
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["health"])  # GET /api/v1/health when included with prefix
async def health() -> dict:
    return {"status": "ok", "service": "community-backend", "version": "0.1.0"}
