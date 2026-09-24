from fastapi import APIRouter

from app.config import settings
from app.logging_config import get_logger

router = APIRouter(tags=["Health"])
logger = get_logger(__name__)


@router.get("/health")
def health_check():
    """Liveness/readiness probe used by Azure App Service and load balancers."""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
    }
