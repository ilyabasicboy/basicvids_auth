from sqlmodel import Field, SQLModel, create_engine


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str = Field(index=True, unique=True)
    first_name: str | None
    last_name: str | None
    age: int | None = None


sqlite_file_name = "basicvids_auth.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)