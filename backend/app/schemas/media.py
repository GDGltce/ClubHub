from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.models.media import PhotoTag


class AlbumCreate(BaseModel):
    club_id: UUID
    event_id: Optional[UUID] = None
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = True


class AlbumUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None


class AlbumOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    club_id: UUID
    event_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    is_public: bool
    created_at: datetime


class PhotoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    album_id: UUID
    uploaded_by_id: UUID
    url: str
    thumbnail_url: Optional[str] = None
    caption: Optional[str] = None
    tag: PhotoTag
    is_cover: bool
    created_at: datetime