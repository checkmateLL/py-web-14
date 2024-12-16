from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import pytest
from main import app
from fastapi.testclient import TestClient

# hardcoded database link
DATABASE_URL = "postgresql+asyncpg://postgres:567234@postgres:5432/contacts_db"

engine = create_async_engine(DATABASE_URL)
SessionTesting = sessionmaker(bind=engine, class_=AsyncSession)

# Test client
client = TestClient(app)

@pytest.mark.asyncio
async def test_user_signup():
    signup_data = {
        "email": "janedoe23@mail.com",
        "password": "password123",
        "username": "janedoe23"
    }

    response = client.post("/api/auth/auth/signup", json=signup_data)
    print(response.json()) 

    assert response.status_code == 201
    assert response.json()["user"]["email"] == signup_data["email"]
