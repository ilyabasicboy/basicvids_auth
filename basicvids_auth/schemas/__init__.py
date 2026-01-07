from sqlmodel import Session, SQLModel, create_engine
from basicvids_auth.schemas.auth import *
from basicvids_auth.schemas.users import *


DATABASE_URL = "sqlite:///database.db"

engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()

create_db_and_tables()