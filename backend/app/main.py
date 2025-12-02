"""
Garden Platform - Backend API

Main FastAPI application with Auth0 authentication, database, and CORS.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# TODO: Import route modules as they are created
from app.api.v1 import users
from app.api.v1.endpoints import gdpr

from app.api.v1.endpoints import videos
from app.api.v1.endpoints import comments

# Garden System endpoints
from app.api.v1.endpoints import seeds, gardens, soil, vines

# MVP endpoints (simplified for user testing)
from app.api.v1.endpoints import mvp_posts


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Growth-oriented community platform with habit tracking, mentorship, and social support",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root health check."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


# Register API v1 routers
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(gdpr.router, prefix=f"{settings.API_V1_PREFIX}/gdpr", tags=["gdpr"])

# Garden System routes
app.include_router(seeds.router, prefix=f"{settings.API_V1_PREFIX}/seeds", tags=["seeds"])
app.include_router(gardens.router, prefix=f"{settings.API_V1_PREFIX}/gardens", tags=["gardens"])
app.include_router(soil.router, prefix=f"{settings.API_V1_PREFIX}/soil", tags=["soil"])
app.include_router(vines.router, prefix=f"{settings.API_V1_PREFIX}/vines", tags=["vines"])

# MVP routes (for user testing - simplified social features)
app.include_router(mvp_posts.router, prefix=f"{settings.API_V1_PREFIX}/mvp", tags=["mvp"])

# Legacy video and comment routes
app.include_router(videos.router, prefix=f"{settings.API_V1_PREFIX}/videos", tags=["videos"])
app.include_router(comments.router, prefix=f"{settings.API_V1_PREFIX}/comments", tags=["comments"])

# TODO: Register additional routers as they are created:
# - flourish (community posts)
# - orchard (connections & messaging)
# - nourishment (daily inspiration)
# - sunlight (gratitude shares)
# - teamup (collaborative projects)
# - support (anonymous support requests)
# - trust (trust verification applications)
# - fellowship (interest-based groups)
# - guardians (moderation & admin)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
