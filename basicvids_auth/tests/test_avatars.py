from pathlib import Path
from tempfile import TemporaryDirectory

import httpx
import pytest
from sqlmodel import Session, delete

from basicvids_auth.schemas.users import Avatar, User
from basicvids_auth.settings import settings
from basicvids_auth.tests import app, engine
from basicvids_auth.utils.auth import create_access_token


temporary_directory = TemporaryDirectory()
settings.DATA_PATH = Path(temporary_directory.name)
pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def request(method: str, url: str, **kwargs):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, url, **kwargs)


class TestAvatars:
    def setup_method(self):
        with Session(engine) as session:
            session.exec(delete(Avatar))
            session.exec(delete(User))
            session.commit()
            user = User(
                username="avatar-user",
                email="avatar@example.com",
                password="password",
                email_confirmed=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            self.user_id = user.id
        self.headers = {"Authorization": f"Bearer {create_access_token(self.user_id)}"}

        settings.avatar_storage_path.mkdir(parents=True, exist_ok=True)
        for path in settings.avatar_storage_path.iterdir():
            path.unlink()

    async def test_registration_avatar_upload_and_download(self):
        response = await request(
            "POST",
            f"/api/v1/avatars/users/{self.user_id}/registration/",
            files={"avatar": ("avatar.png", b"fake-avatar-bytes", "image/png")},
        )

        assert response.status_code == 201
        assert response.json()["user_id"] == self.user_id

        response = await request("GET", f"/api/v1/avatars/users/{self.user_id}/image/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert response.content == b"fake-avatar-bytes"

    async def test_registration_avatar_requires_existing_user(self):
        response = await request(
            "POST",
            "/api/v1/avatars/users/999/registration/",
            files={"avatar": ("avatar.png", b"fake-avatar-bytes", "image/png")},
        )

        assert response.status_code == 404

    async def test_current_user_can_replace_and_delete_avatar(self):
        response = await request(
            "PUT",
            "/api/v1/avatars/me/",
            headers=self.headers,
            files={"avatar": ("avatar.png", b"first-avatar", "image/png")},
        )

        assert response.status_code == 200

        response = await request(
            "PUT",
            "/api/v1/avatars/me/",
            headers=self.headers,
            files={"avatar": ("avatar.jpg", b"second-avatar", "image/jpeg")},
        )

        assert response.status_code == 200
        assert len(list(settings.avatar_storage_path.iterdir())) == 1

        response = await request("DELETE", "/api/v1/avatars/me/", headers=self.headers)

        assert response.status_code == 200
        assert list(settings.avatar_storage_path.iterdir()) == []

    async def test_missing_avatar_returns_placeholder(self):
        response = await request("GET", f"/api/v1/avatars/users/{self.user_id}/image/")

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/svg+xml"
        assert "<svg" in response.text

    async def test_deleting_user_deletes_stored_avatar(self):
        await request(
            "PUT",
            "/api/v1/avatars/me/",
            headers=self.headers,
            files={"avatar": ("avatar.png", b"avatar", "image/png")},
        )

        response = await request("DELETE", "/api/v1/users/delete/", headers=self.headers)

        assert response.status_code == 200
        with Session(engine) as session:
            assert session.get(Avatar, self.user_id) is None
        assert list(settings.avatar_storage_path.iterdir()) == []
