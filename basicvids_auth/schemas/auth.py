from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import DateTime
from datetime import datetime, timezone
from typing import Optional
import uuid


class RefreshToken(SQLModel, table=True):

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    user_id: int = Field(
        foreign_key="user.id",
        index=True,
        nullable=False,
    )
    expires_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        nullable=False,
    )
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    revoked_at: Optional[datetime] = Field(
        sa_type=DateTime(timezone=True),
        default=None,
    )

    # relationship
    user: Optional["User"] = Relationship(back_populates="refresh_tokens")
