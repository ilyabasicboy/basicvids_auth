from typing import Union, Optional

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, constr, model_validator

from sqlmodel import select, Session

from schemas import get_session, User as UserDB


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


class UserCreate(BaseModel):
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    password: constr(max_length=72)

    @model_validator(mode='before')
    def check_unique(cls, values):
        username = values.get("username")
        email = values.get("email")
        session = next(get_session())
        existing_user = session.exec(
            select(UserDB).where((UserDB.username == username) | (UserDB.email == email))
        ).first()
        if existing_user:
            raise ValueError("Username or email already exists")
        return values
    