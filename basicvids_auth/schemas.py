from sqlmodel import Field, Session, SQLModel, create_engine
from typing import Optional
from pydantic import EmailStr


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(max_length=100)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    email: EmailStr = Field(max_length=100)
    password: str = Field(max_length=100)
    is_admin: bool = Field(default=False)


DATABASE_URL = "postgresql+psycopg://ilya@/basicvids_auth"


engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()