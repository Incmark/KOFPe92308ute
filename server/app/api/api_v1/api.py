from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, random

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(random.router, prefix="/random", tags=["random"])