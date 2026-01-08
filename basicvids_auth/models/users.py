from typing import Optional

from pydantic import BaseModel, EmailStr, constr


class User(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    password: str
    is_admin: bool = False


class PublicUser(BaseModel):
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    is_admin: bool = False


class FilterUser(BaseModel):
    id: Optional[int] = None
    username: str | None = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr | None = None
    is_admin: bool | None = None


class UserCreate(BaseModel):
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    password: constr(max_length=72)
    

class AdminCreate(BaseModel):
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    password: constr(max_length=72)
    is_admin: bool = True