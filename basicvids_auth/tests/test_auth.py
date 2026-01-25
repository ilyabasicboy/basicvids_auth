from sqlmodel import Session, select, delete

from basicvids_auth.schemas.users import User as UserDB 
from basicvids_auth.tests import engine, client
from basicvids_auth.utils.auth import create_access_token, create_refresh_token
from basicvids_auth.utils.password import hash_password
from basicvids_auth.models.auth import TokenResponse
from basicvids_auth.schemas.auth import RefreshToken
from basicvids_auth.settings import settings

from datetime import datetime, timedelta, timezone

from abc import ABC


class BaseTestAuth(ABC):

    def setup_method(self):
        """Runs BEFORE each test in this class"""
        # Clear table before each test

        self.payload = {
            "username": "test",
            "email": "test@example.com",
            "password": hash_password("secret123"),
            "first_name": "Test",
            "last_name": "Test",
        }

        with Session(engine) as session:
            session.exec(delete(UserDB))
            session.commit()

            # create test admin user
            self.test_user = UserDB(**self.payload)
            session.add(self.test_user)
            session.commit()
            session.refresh(self.test_user)

    def teardown_method(self):
        """Runs AFTER each test if needed"""
        pass


class TestAuthLogin(BaseTestAuth):
    method_url = "api/v1/auth/login/"

    def test_login_username_success(self):
        data = {
            "password": "secret123",
            "identifier": "test"
        }

        response = client.post(self.method_url, json=data)
        assert response.status_code == 201

        response_data = response.json()
        assert TokenResponse(**response_data)

    def test_login_email_success(self):
        data = {
            "password": "secret123",
            "identifier": "test@example.com"
        }

        response = client.post(self.method_url, json=data)
        assert response.status_code == 201

        response_data = response.json()
        assert TokenResponse(**response_data)

    def test_login_wrong_data(self):
        data = {
            "password": "secret123",
            # "identifier": "test@example.com"
        }

        response = client.post(self.method_url, json=data)
        assert response.status_code == 422

    def test_login_not_authorized(self):
        data = {
            "password": "secret123",
            "identifier": "unknown"
        }

        response = client.post(self.method_url, json=data)
        assert response.status_code == 401


class TestAuthRefresh(BaseTestAuth):
    method_url = 'api/v1/auth/refresh/'

    def setup_method(self):
        super().setup_method()

        iat = datetime.now(timezone.utc)
        exp = iat + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_token = RefreshToken(
            user_id=self.test_user.id,
            expires_at=exp,
            created_at=iat
        )
        
        with Session(engine) as session:
            session.add(refresh_token)
            session.commit()
            session.refresh(refresh_token)

        self.refresh_token = create_refresh_token(self.test_user.id, refresh_token.id)
    
    def test_refresh_success(self):
        data = {
            "refresh_token": self.refresh_token
        }
        response = client.post(self.method_url, json=data)
        response_data = response.json()
        
        assert response.status_code == 200

        assert TokenResponse(**response_data)

    def test_refresh_incorrect_token_type(self):

        access_token = create_access_token(self.test_user.id)
        data = {
            "refresh_token": access_token 
        }
        response = client.post(self.method_url, json=data)

        assert response.status_code == 401

    def test_refresh_incorrect_data(self):
        data = {}
        response = client.post(self.method_url, json=data)
        
        assert response.status_code == 422

    def test_refresh_incorrect_token(self):
        data = {
            "refresh_token": "wrongtoken"
        }
        response = client.post(self.method_url, json=data)

        assert response.status_code == 401


class TestAuthLogout(BaseTestAuth):
    method_url = 'api/v1/auth/logout/'

    def setup_method(self):
        super().setup_method()

        iat = datetime.now(timezone.utc)
        exp = iat + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_token = RefreshToken(
            user_id=self.test_user.id,
            expires_at=exp,
            created_at=iat
        )
        
        with Session(engine) as session:
            session.add(refresh_token)
            session.commit()
            session.refresh(refresh_token)

        self.refresh_token = create_refresh_token(self.test_user.id, refresh_token.id)

    def test_logout_success(self):
        data = {
            "refresh_token": self.refresh_token
        }
        response = client.post(self.method_url, json=data)
        
        assert response.status_code == 200

    def test_refresh_incorrect_token_type(self):

        access_token = create_access_token(self.test_user.id)
        data = {
            "refresh_token": access_token 
        }
        response = client.post(self.method_url, json=data)

        assert response.status_code == 401

    def test_refresh_incorrect_data(self):
        data = {}
        response = client.post(self.method_url, json=data)
        
        assert response.status_code == 422

    def test_refresh_incorrect_token(self):
        data = {
            "refresh_token": "wrongtoken"
        }
        response = client.post(self.method_url, json=data)

        assert response.status_code == 401