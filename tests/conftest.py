import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use a try-except block to handle potential import issues
try:
    from main import app
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
def client(session):
    """
    Creates a test client that uses the override_get_db for each test.
    """
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def user_data():
    return {
        "email": "testuser@example.com",
        "password": "securepassword",
        "username": "testuser"
    }