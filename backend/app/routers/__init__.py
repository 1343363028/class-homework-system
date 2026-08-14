"""路由汇总"""
from fastapi import APIRouter
from . import auth, subject, homework

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(subject.router)
api_router.include_router(homework.router)
