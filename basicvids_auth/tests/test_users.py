from sqlmodel import Session, select, delete

from basicvids_auth.schemas.users import User as UserDB 
from basicvids_auth.schemas.users import EmailCode as EmailCodeDB
from basicvids_auth.tests import engine, client
from basicvids_auth.utils.auth import create_access_token
from basicvids_auth.utils.password import hash_password, verify_password
from basicvids_auth.models.users import PublicUser

from abc import ABC


class BaseTestUsers(ABC):

    def setup_method(self):
        """Runs BEFORE each test in this class"""
        # Clear table before each test

        self.payload = {
            "username": "test",
            "email": "test@example.com",
            "password": "secret123",
            "first_name": "Test",
            "last_name": "Test",
        }

        admin_payload = {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin",
            "first_name": "Admin",
            "last_name": "Admin",
            "is_admin": True,
            "email_confirmed": True,
        }

        with Session(engine) as session:
            session.exec(delete(EmailCodeDB))
            session.exec(delete(UserDB))
            session.commit()

            # create test admin user
            admin_user = UserDB(**admin_payload)
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)

        token = create_access_token(admin_user.id)

        self.headers = {
            'Authorization': 'Bearer {}'.format(token)
        }

    def teardown_method(self):
        """Runs AFTER each test if needed"""
        pass


class TestUsersList(BaseTestUsers):

    method_url = '/api/v1/users/'

    def setup_method(self):
        super().setup_method()
        
        self.test_user = UserDB(**self.payload)

        with Session(engine) as session:
            session.add(self.test_user)
            session.commit()
            session.refresh(self.test_user)

    def test_users_list_success(self):
        response = client.get(self.method_url, headers=self.headers)
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) != 0

        user_data = response_data[0]
        assert PublicUser(**user_data)

    def test_users_list_pagination(self):
        params = {
            "offset": 0,
            "limit": 1
        }
        response = client.get(
            self.method_url,
            params=params,
            headers=self.headers    
        )
        assert response.status_code == 200

        response_data = response.json()

        assert len(response_data) == 1

    def test_users_list_pagination_empty(self):

        params = {
            "offset": 2,
            "limit": 1
        }
        response = client.get(
            self.method_url,
            params=params,
            headers=self.headers
        )
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) == 0

    def test_users_list_filter(self):
        params = {
            "username": self.payload['username']
        }

        response = client.get(
            self.method_url,
            params=params,
            headers=self.headers
        )
        assert response.status_code == 200

        response_data = response.json()

        assert len(response_data) == 1

    def test_users_list_filter_empty(self):
        params = {
            # wrong username
            "username": "abracadabra"
        }

        response = client.get(
            self.method_url,
            params=params,
            headers=self.headers
        )
        assert response.status_code == 200

        response_data = response.json()

        assert len(response_data) == 0

    def test_users_list_no_permissions(self):
        test_token = create_access_token(self.test_user.id)
        test_headers = {
            'Authorization': 'Bearer {}'.format(test_token)
        }
        response = client.get(self.method_url, headers=test_headers)
        assert response.status_code == 403


class TestUsersCreate(BaseTestUsers):
    
    method_url = "/api/v1/users/create/"

    def test_create_user_success(self):

        response = client.post(
            self.method_url,
            json=self.payload
        )
        response_data = response.json()
        assert response.status_code == 201

        self.payload.pop('password')
        for key, value in self.payload.items():
            assert value == response_data[key]
        assert response_data["email_confirmed"] is False

        with Session(engine) as session:
            user = session.exec(select(UserDB).where(UserDB.email == "test@example.com")).first()
            assert user is not None
            assert user.email_confirmed is False
            email_code = session.exec(select(EmailCodeDB).where(EmailCodeDB.email == "test@example.com")).first()
            assert email_code is not None

    def test_confirm_email_success(self):
        response = client.post(self.method_url, json=self.payload)
        assert response.status_code == 201

        with Session(engine) as session:
            email_code = session.exec(select(EmailCodeDB).where(EmailCodeDB.email == "test@example.com")).first()
            code = email_code.code

        response = client.post(
            "/api/v1/users/confirm/email/",
            json={
                "email": "test@example.com",
                "code": code,
            },
        )

        assert response.status_code == 200
        assert response.json()["email_confirmed"] is True

    def test_confirm_email_rejects_wrong_code(self):
        response = client.post(self.method_url, json=self.payload)
        assert response.status_code == 201

        response = client.post(
            "/api/v1/users/confirm/email/",
            json={
                "email": "test@example.com",
                "code": "000000",
            },
        )

        assert response.status_code == 400

    def test_create_user_invalid_data(self):
        
        # Remove required field from payload
        self.payload.pop('username')
        
        response = client.post(self.method_url, json=self.payload)
        assert response.status_code == 422

    def test_create_user_duplicate(self):

        response = client.post(self.method_url, json=self.payload)
        assert response.status_code == 201

        # try to create duplicate
        response = client.post(self.method_url, json=self.payload)
        
        assert response.status_code == 400

    def test_create_user_duplicate_username(self):
        existing_user = self.payload.copy()
        existing_user["email"] = "existing@example.com"
        response = client.post(self.method_url, json=existing_user)
        assert response.status_code == 201

        duplicate_username_payload = self.payload.copy()
        duplicate_username_payload["email"] = "new@example.com"

        response = client.post(self.method_url, json=duplicate_username_payload)

        assert response.status_code == 400

    def test_create_user_duplicate_email(self):
        existing_user = self.payload.copy()
        existing_user["username"] = "existing-user"
        response = client.post(self.method_url, json=existing_user)
        assert response.status_code == 201

        duplicate_email_payload = self.payload.copy()
        duplicate_email_payload["username"] = "new-user"

        response = client.post(self.method_url, json=duplicate_email_payload)

        assert response.status_code == 400


class TestUserDelete(BaseTestUsers):
    method_url = "/api/v1/users/delete"

    def setup_method(self):
        super().setup_method()

        test_user = UserDB(**self.payload)

        with Session(engine) as session:
            session.add(test_user)
            session.commit()
            session.refresh(test_user)

    def test_delete_user(self):
        response = client.delete(
            self.method_url,
            headers=self.headers
        )

        assert response.status_code == 200

    def test_delete_user_unauthorized(self):
        response = client.delete(
            self.method_url,
            headers={}
        )

        assert response.status_code == 401


class TestUserDeleteById(BaseTestUsers):
    method_url = "/api/v1/users/delete"

    def setup_method(self):
        super().setup_method()

        self.test_user = UserDB(**self.payload)

        with Session(engine) as session:
            session.add(self.test_user)
            session.commit()
            session.refresh(self.test_user)

        self.method_url = f"/api/v1/users/delete/{self.test_user.id}"

    def test_delete_user(self):
        response = client.delete(
            self.method_url,
            headers=self.headers
        )

        assert response.status_code == 200

    def test_delete_user_unauthorized(self):
        response = client.delete(
            self.method_url,
            headers={}
        )

        assert response.status_code == 401

    def test_delete_user_no_permissions(self):
        test_token = create_access_token(self.test_user.id)
        test_headers = {
            'Authorization': 'Bearer {}'.format(test_token)
        }
        response = client.delete(self.method_url, headers=test_headers)
        assert response.status_code == 403


class TestUserDetail(BaseTestUsers):
    method_url = None

    def setup_method(self):
        super().setup_method()

        test_user = UserDB(**self.payload)

        with Session(engine) as session:
            session.add(test_user)
            session.commit()
            session.refresh(test_user)

        token = create_access_token(test_user.id)
        self.headers = {
            'Authorization': 'Bearer {}'.format(token)
        }

        self.method_url = f"/api/v1/users/detail/"

    def test_detail_user_success(self):
        response = client.get(
            self.method_url,
            headers=self.headers
        )
        assert response.status_code == 200

        response_data = response.json()

        self.payload.pop('password')
        for key, value in self.payload.items():
            assert value == response_data[key]

    def test_detail_user_not_authorized(self):
        response = client.get(
            self.method_url,
            headers={}
        )
        assert response.status_code == 401


class TestUserChange(BaseTestUsers):
    method_url = "/api/v1/users/change/"

    def setup_method(self):
        super().setup_method()

        self.test_user = UserDB(**self.payload)

        with Session(engine) as session:
            session.add(self.test_user)
            session.commit()
            session.refresh(self.test_user)

        token = create_access_token(self.test_user.id)
        self.user_headers = {
            'Authorization': 'Bearer {}'.format(token)
        }

    def test_change_user_success(self):
        response = client.patch(
            self.method_url,
            json={
                "first_name": "Changed",
                "last_name": "User",
            },
            headers=self.user_headers,
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["first_name"] == "Changed"
        assert response_data["last_name"] == "User"
        assert response_data["username"] == self.payload["username"]
        assert response_data["email"] == self.payload["email"]

    def test_change_user_not_authorized(self):
        response = client.patch(
            self.method_url,
            json={
                "first_name": "Changed",
                "last_name": "User",
            },
            headers={},
        )

        assert response.status_code == 401


class TestUserPasswordChange(BaseTestUsers):
    method_url = "/api/v1/users/change/password/"

    def setup_method(self):
        super().setup_method()

        self.test_user = UserDB(**{
            **self.payload,
            "password": hash_password(self.payload["password"]),
        })

        with Session(engine) as session:
            session.add(self.test_user)
            session.commit()
            session.refresh(self.test_user)

        token = create_access_token(self.test_user.id)
        self.user_headers = {
            'Authorization': 'Bearer {}'.format(token)
        }

    def test_change_user_password_success(self):
        response = client.patch(
            self.method_url,
            json={
                "old_password": self.payload["password"],
                "new_password": "new-secret",
            },
            headers=self.user_headers,
        )

        assert response.status_code == 200
        assert response.json() == {"message": "Password changed successfully"}

        with Session(engine) as session:
            user = session.get(UserDB, self.test_user.id)
            assert verify_password("new-secret", user.password)

    def test_change_user_password_rejects_wrong_old_password(self):
        response = client.patch(
            self.method_url,
            json={
                "old_password": "wrong-password",
                "new_password": "new-secret",
            },
            headers=self.user_headers,
        )

        assert response.status_code == 400

    def test_change_user_password_not_authorized(self):
        response = client.patch(
            self.method_url,
            json={
                "old_password": self.payload["password"],
                "new_password": "new-secret",
            },
            headers={},
        )

        assert response.status_code == 401


class TestUserDetailById(BaseTestUsers):
    method_url = None

    def setup_method(self):
        super().setup_method()

        self.test_user = UserDB(**self.payload)

        with Session(engine) as session:
            session.add(self.test_user)
            session.commit()
            session.refresh(self.test_user)

        self.method_url = f"/api/v1/users/detail/{self.test_user.id}"

    def test_detail_user_success(self):
        response = client.get(
            self.method_url,
            headers=self.headers
        )
        assert response.status_code == 200

        response_data = response.json()

        self.payload.pop('password')
        for key, value in self.payload.items():
            assert value == response_data[key]

    def test_detail_user_not_authorized(self):
        response = client.get(
            self.method_url,
            headers={}
        )
        assert response.status_code == 401

    def test_detail_user_no_permissions(self):
        token = create_access_token(self.test_user.id)
        headers = {
            'Authorization':'Bearer {}'.format(token)
        }
        response = client.get(
            self.method_url,
            headers=headers
        )
        assert response.status_code == 403
