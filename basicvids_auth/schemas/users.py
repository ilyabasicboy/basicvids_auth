from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from pydantic import EmailStr


class User(SQLModel, table=True):

    id: int = Field(default=None, primary_key=True)
    username: str = Field(max_length=100, unique=True)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    email: EmailStr = Field(max_length=100, unique=True)
    password: str = Field(max_length=72)
    is_admin: bool = Field(default=False)

    refresh_tokens: List["RefreshToken"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
