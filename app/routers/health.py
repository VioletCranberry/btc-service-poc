from fastapi import APIRouter, status


def health_router() -> APIRouter:
    """
    Creates a router for the health check endpoint.

    Returns:
        APIRouter: The configured FastAPI router for health check.
    """
    router = APIRouter()

    @router.get(
        "/health",
        status_code=status.HTTP_200_OK,
        tags=["health"],
        summary="Health Check",
        description="Endpoint to check if the application is running as expected.",
    )
    def health_check():
        return {"status": "healthy"}

    return router
