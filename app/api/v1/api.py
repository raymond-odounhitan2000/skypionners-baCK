from fastapi import APIRouter
from app.api.v1.endpoints import auth, health, users, email

api_router = APIRouter()
api_router.include_router(auth.router, prefix="", tags=["authentication"])
api_router.include_router(email.router, prefix="/email", tags=["email"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
