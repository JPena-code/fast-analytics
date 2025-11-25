from fastapi import status
from fastapi.routing import APIRouter

from . import events
from .health import health_check

__version__ = "1.0"
VERSION = f"v{__version__}"

router = APIRouter(prefix=f"/api/{VERSION}")

router.include_router(events.router, prefix="/events", tags=["events", VERSION])

router.add_api_route(
    "/healthzcheck",
    health_check,
    methods=["GET", "HEAD"],
    status_code=status.HTTP_200_OK,
    tags=["health"],
)

__all__ = ["router"]
