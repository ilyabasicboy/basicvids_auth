from typing import Union, Optional

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    password: str
    is_admin: bool = False


class PublicUser(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    is_admin: bool = False
