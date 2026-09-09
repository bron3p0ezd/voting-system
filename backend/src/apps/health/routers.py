from fastapi import APIRouter

from settings.urls import BaseUrls


router = APIRouter(
    prefix="/api/health",
    tags=["Health"],
)


@router.get(
    "",
    name=BaseUrls.get_health,
)
async def health_check():
    return {"status": "healthy"}
