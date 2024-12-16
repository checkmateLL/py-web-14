import unittest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from main import app
from src.repository.users import create_user

client = TestClient(app)

class TestRoutesAuth(unittest.TestCase):
    def test_signup_successful(self):
        # Prepare signup data
        signup_data = {
            "email": "janedoe@mail.com",
            "password": "password123",
            "username": "janedoe",
        }

        # Mock repository
        app.dependency_overrides[create_user] = AsyncMock(return_value={
            "email": signup_data["email"],
            "username": signup_data["username"],
            "confirmed": False
        })

        # Perform the POST request
        response = client.post("/api/auth/auth/signup", json=signup_data)

        # Assertions
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data["user"]["email"], "janedoe@mail.com")
        self.assertEqual(response_data["user"]["confirmed"], False)

if __name__ == '__main__':
    unittest.main()
