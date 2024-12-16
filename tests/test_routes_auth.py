import pytest
import jwt
from unittest.mock import AsyncMock, patch, Mock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from main import app 
from src.database.models import Base
from src.database.db import get_db
from src.services.auth_service_class import AuthService
from src.services.auth_service_class import get_auth_service

# SQLite in-memory database for tests
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

SECRET_KEY = "1957ahyse3hb"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# async engine and session
engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Authentication service for tests
auth_service_instance = AuthService(
    secret_key=SECRET_KEY,
    algorithm=ALGORITHM,
    access_token_expire_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
)

def get_test_auth_service():
    return auth_service_instance

@pytest.fixture(scope="function")
async def session():
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Recreate all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create new session
    async with TestingSessionLocal() as session:
        yield session
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
def client(session):
    def override_get_db():
        yield session

    def override_get_auth_service():
        return auth_service_instance

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_auth_service] = override_get_auth_service
    
    client = TestClient(app)
    yield client
    
    app.dependency_overrides.clear()

# Mock email service to prevent actual email sending
@pytest.fixture
def mock_email_service(mocker):
    mock_service = mocker.Mock()
    mock_service.send_email = mocker.AsyncMock(return_value=True)
    return mock_service

# Test data
user_data = {
    "username": "unique_username3", 
    "email": "unique3@example.com", 
    "password": "password123"
}

def test_create_user(client, mock_email_service):
    # Patch the email service
    with patch('src.services.email.email_service.send_email', mock_email_service.send_email):
        response = client.post("/api/auth/auth/signup", json=user_data)
        assert response.status_code == 201  # Changed from 200 to 201 based on your routes
        assert response.json()["user"]["email"] == user_data["email"]

def test_login(client, mock_email_service):
    # First, create a user
    with patch('src.services.email.email_service.send_email', mock_email_service.send_email):
        signup_response = client.post("/api/auth/auth/signup", json=user_data)
        print("Signup response:", signup_response.json())
        assert signup_response.status_code == 201

    # Then attempt login
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/auth/auth/login", json=login_data)
    
    # Print detailed error information
    print("Login response status code:", response.status_code)
    print("Login response content:", response.json())
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()