from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    identifier: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = None
