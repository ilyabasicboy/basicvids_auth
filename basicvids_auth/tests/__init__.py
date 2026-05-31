import asyncio

import httpx

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from basicvids_auth.main import app
from basicvids_auth.schemas import get_session


# Create test db (in-memory)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SQLModel.metadata.create_all(engine)

async def override_get_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session


class SyncASGIClient:
    def __init__(self, app, base_url: str = "http://test"):
        self.app = app
        self.base_url = base_url

    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        async def call():
            transport = httpx.ASGITransport(app=self.app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url=self.base_url,
                follow_redirects=True,
            ) as async_client:
                return await async_client.request(method, url, **kwargs)

        return asyncio.run(call())

    def get(self, url: str, **kwargs) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        return self.request("POST", url, **kwargs)

    def patch(self, url: str, **kwargs) -> httpx.Response:
        return self.request("PATCH", url, **kwargs)

    def put(self, url: str, **kwargs) -> httpx.Response:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> httpx.Response:
        return self.request("DELETE", url, **kwargs)


client = SyncASGIClient(app)
