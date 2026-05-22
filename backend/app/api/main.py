from fastapi import APIRouter
from app.api.routes import login, user, project

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(user.router)
api_router.include_router(project.router)
