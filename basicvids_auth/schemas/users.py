from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from pydantic import EmailStr
from sqlalchemy import DateTime
from datetime import datetime, timezone
import uuid


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):

    id: int = Field(default=None, primary_key=True)
    username: str = Field(max_length=100, unique=True)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    email: EmailStr = Field(max_length=100, unique=True)
    password: str = Field(max_length=72)
    is_admin: bool = Field(default=False)
    email_confirmed: bool = Field(default=False)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=utc_now,
        nullable=False,
    )

    refresh_tokens: List["RefreshToken"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class EmailCode(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    email: EmailStr = Field(max_length=100, index=True)
    code: str = Field(max_length=20)
    expires_at: datetime = Field(sa_type=DateTime(timezone=True), nullable=False)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=utc_now,
        nullable=False,
    )
