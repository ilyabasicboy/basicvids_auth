from sqlmodel import Session, select, delete

from basicvids_auth.schemas.users import User as UserDB 
from basicvids_auth.tests import engine, client
from basicvids_auth.utils.auth import create_access_token

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
            "is_admin": True
        }

        with Session(engine) as session:
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
        test_headers = self.headers = {
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

        with Session(engine) as session:
            user = session.exec(select(UserDB).where(UserDB.email == "test@example.com")).first()
            assert user is not None

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


class TestUserDelete(BaseTestUsers):
    method_url = "/api/v1/users/delete"

    def setup_method(self):
        super().setup_method()

        test_user = UserDB(**self.payload)

        with Session(engine) as session:
            session.add(test_user)
            session.commit()
            session.refresh(test_user)

        self.method_url = f"/api/v1/users/delete/{test_user.id}"

    def test_delete_user(self):
        response = client.delete(
            self.method_url,
            headers=self.headers
        )

        assert response.status_code == 200

    # def test_delete_user_404(self):

    #     response = client.delete("/api/v1/users/999")

    #     assert response.status_code == 404


class TestUserDetail(BaseTestUsers):
    method_url = None

    def setup_method(self):
        super().setup_method()

        test_user = UserDB(**self.payload)

        with Session(engine) as session:
            session.add(test_user)
            session.commit()
            session.refresh(test_user)

        self.method_url = f"/api/v1/users/detail/{test_user.id}"

    def test_detail_user(self):
        response = client.get(
            self.method_url,
            headers=self.headers
        )
        assert response.status_code == 200

        response_data = response.json()

        self.payload.pop('password')
        for key, value in self.payload.items():
            assert value == response_data[key]