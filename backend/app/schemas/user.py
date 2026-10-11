"""
User schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from app.models.user import GlobalRole


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    global_role: GlobalRole
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    global_role: Optional[GlobalRole] = None
