from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.health.routers import router as health_router

from config import settings


app = FastAPI(
    docs_url=settings.DOCS_URL_ENABLED,
    redoc_url=settings.REDOC_URL_ENABLED,
    openapi_url=settings.OPENAPI_URL_ENABLED,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["OPTIONS", "POST", "GET", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
app.include_router(health_router)


api_router = APIRouter(prefix="/api/v1")

app.include_router(api_router)
