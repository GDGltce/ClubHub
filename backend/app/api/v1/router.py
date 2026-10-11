"""
V1 API router – aggregates all endpoint routers
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, institutions, clubs, memberships, events, documents, meetings, notifications, photos
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(institutions.router)
api_router.include_router(clubs.router)
api_router.include_router(memberships.router)
api_router.include_router(events.router)
api_router.include_router(documents.router)
api_router.include_router(meetings.router)
api_router.include_router(photos.router)
