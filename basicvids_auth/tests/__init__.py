from fastapi.testclient import TestClient

from sqlmodel import SQLModel, Session, create_engine

from basicvids_auth.main import app
from basicvids_auth.schemas import get_session


# Create test db
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SQLModel.metadata.create_all(engine)

def override_get_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

# Create client
client = TestClient(app)