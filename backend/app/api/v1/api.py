from fastapi import APIRouter
from app.api.v1.endpoints import ingestion, tryon, search

api_router = APIRouter()

api_router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(tryon.router, prefix="/tryon", tags=["tryon"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
