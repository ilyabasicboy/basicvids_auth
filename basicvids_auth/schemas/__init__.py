from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel, create_engine
from basicvids_auth.schemas.auth import *
from basicvids_auth.schemas.users import *
from basicvids_auth.settings import settings


DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    settings.DATA_PATH.mkdir(parents=True, exist_ok=True)
    settings.avatar_storage_path.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)
    migrate_user_email_confirmation()


def migrate_user_email_confirmation():
    inspector = inspect(engine)
    if "user" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("user")}
    with engine.begin() as connection:
        if "email_confirmed" not in columns:
            connection.execute(text("ALTER TABLE user ADD COLUMN email_confirmed BOOLEAN DEFAULT 1 NOT NULL"))
        if "created_at" not in columns:
            connection.execute(text("ALTER TABLE user ADD COLUMN created_at DATETIME"))


def get_session():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()
