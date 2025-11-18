"""
Garden Platform - Backend API

Main FastAPI application with Auth0 authentication, database, and CORS.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# TODO: Import route modules as they are created
from app.api.v1 import users, garden


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
app.include_router(garden.router, prefix=settings.API_V1_PREFIX)

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
