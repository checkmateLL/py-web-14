import os
import sys
from main import app
from src.services.auth_service_class import get_auth_service


# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# try-except block to handle potential import issues
try:
    
    from src.database.models import Base
    from src.database.db import get_db
except ImportError as e:
    print(f"Import error: {e}")
    print("Current Python path:", sys.path)
    raise

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def session():
    """
    Creates a new database session for each test function.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def mock_auth_service():
    from src.services.auth_service_class import AuthService
    return AuthService(
        secret_key="1957ahyse3hb",
        algorithm="HS256",
        access_token_expire_minutes=30,
    )

@pytest.fixture(scope="function")
def client(session, mock_auth_service):
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def user_data():
    return {
        "email": "testuser@example.com",
        "password": "securepassword",
        "username": "testuser"
    }

@pytest.fixture(scope="function")
def mock_email_service(monkeypatch):
    def mock_send_email(*args, **kwargs):
        return True
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)