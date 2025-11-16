from typing import Union, Optional

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, constr, model_validator

from sqlmodel import select, Session

from basicvids_auth.schemas import get_session, User as UserDB


class User(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    password: str
    is_admin: bool = False


class PublicUser(BaseModel):
    username: str | None = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr | None = None
    is_admin: bool = False


class UserCreate(BaseModel):
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    password: constr(max_length=72)
    