from app.api.v1.endpoints import lifecycle
api_router.include_router(
    lifecycle.router,
    prefix="/lifecycle",
    tags=["lifecycle"]
)
