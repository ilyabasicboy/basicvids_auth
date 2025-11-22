from sqlmodel import Session, SQLModel, create_engine


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


if __name__ == "__main__":
    create_db_and_tables()