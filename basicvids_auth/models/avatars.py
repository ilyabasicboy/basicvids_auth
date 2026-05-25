from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AvatarPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    storage_backend: str
    content_type: str
    size_bytes: int
    created_at: datetime
    updated_at: datetime


class AvatarDeleteResponse(BaseModel):
    message: str
