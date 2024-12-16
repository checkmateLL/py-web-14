import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from main import app 
from src.database.models import Base
from src.database.db import get_db
#from src.services.auth import AuthService
from src.services.auth import _get_auth_service

# SQLite in-memory database for tests
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Mock service for auth
class MockAuthService:
    def get_password_hash(self, password) -> str:
        return f"hashed-{password}"

    def verify_password(self, plain_password, hashed_password) -> bool:
        return hashed_password == f"hashed-{plain_password}"

    async def create_access_token(self, data):
        return "mock_access_token"

    async def create_refresh_token(self, data):
        return "mock_refresh_token"

@pytest.fixture
def mock_email_service(mocker):
    email_service = mocker.patch("src.services.email.EmailService")
    email_service.send_email = AsyncMock(return_value=None)
    return email_service

@pytest.fixture(scope="function")
async def session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        yield session
    await engine.dispose()


@pytest.fixture
def mock_auth_service():    
    return MockAuthService()


@pytest.fixture(scope="function")
def client(session, mock_auth_service):
    app.dependency_overrides[_get_auth_service] = lambda: mock_auth_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


user_data = {"username": "unique_username", "email": "unique@example.com", "password": "password"}


# Test cases
def test_create_user(client, session, user_data, mock_auth_service):
    response = client.post("/api/auth/auth/signup", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]


def test_login(client, session, user_data, mock_auth_service):
    # First, create a user
    client.post("/api/auth/auth/signup", json=user_data)
    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = client.post("/api/auth/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
