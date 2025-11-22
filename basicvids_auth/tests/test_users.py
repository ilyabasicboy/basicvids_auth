from fastapi.testclient import TestClient

from sqlmodel import SQLModel, Session, create_engine, select, delete

from basicvids_auth.main import app
from basicvids_auth.schemas import get_session
from basicvids_auth.schemas.users import User as UserDB 

from abc import ABC

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

        with Session(engine) as session:
            session.exec(delete(UserDB))
            session.commit()

    def teardown_method(self):
        """Runs AFTER each test if needed"""
        pass


class TestUsersList(BaseTestUsers):

    method_url = '/api/v1/users/'

    def setup_method(self):
        super().setup_method()

        
        test_user = UserDB(**self.payload)

        with Session(engine) as session:
            session.add(test_user)
            session.commit()

    def test_users_list_success(self):
        response = client.get(self.method_url)
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) != 0

    def test_users_list_pagination(self):
        params = {
            "offset": 0,
            "limit": 1
        }
        response = client.get(self.method_url, params=params)
        assert response.status_code == 200

        response_data = response.json()

        assert len(response_data) == 1

    def test_users_list_pagination_empty(self):

        params = {
            "offset": 1,
            "limit": 1
        }
        response = client.get(self.method_url, params=params)
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) == 0

    def test_users_list_filter(self):
        params = {
            "username": self.payload['username']
        }

        response = client.get(self.method_url, params=params)
        assert response.status_code == 200

        response_data = response.json()

        assert len(response_data) == 1

    def test_users_list_filter_empty(self):
        params = {
            # wrong username
            "username": "abracadabra"
        }

        response = client.get(self.method_url, params=params)
        assert response.status_code == 200

        response_data = response.json()

        assert len(response_data) == 0


class TestUsersCreate(BaseTestUsers):
    
    method_url = "/api/v1/users/create/"

    def test_create_user_success(self):

        response = client.post(self.method_url, json=self.payload)
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
    method_url = None

    def setup_method(self):
        super().setup_method()

        test_user = UserDB(**self.payload)

        with Session(engine) as session:
            session.add(test_user)
            session.commit()
            session.refresh(test_user)

        self.method_url = f"/api/v1/users/{test_user.id}"

    def test_delete_user(self):

        response = client.delete(self.method_url)

        assert response.status_code == 200

    def test_delete_user_404(self):

        response = client.delete("/api/v1/users/999")

        assert response.status_code == 404


class TestUserDetail(BaseTestUsers):
    method_url = "/api/v1/users/1"

    def setup_method(self):
        super().setup_method()

        test_user = UserDB(**self.payload)

        with Session(engine) as session:
            session.add(test_user)
            session.commit()
            session.refresh(test_user)

    def test_detail_user(self):

        response = client.get(self.method_url)

        assert response.status_code == 200

        response_data = response.json()

        self.payload.pop('password')
        for key, value in self.payload.items():
            assert value == response_data[key]