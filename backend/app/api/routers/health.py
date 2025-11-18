"""
Health check router (no auth required)
"""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "ok",
        "service": "community-api",
        "version": "0.1.0"
    }
