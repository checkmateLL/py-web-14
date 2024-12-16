import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_create_contact():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Test user login to get a token
        token = "Bearer YOUR_TEST_TOKEN"

        # Request payload
        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@example.com",
            "phone": "1234567890",
            "birthday": "2000-01-01",
            "additional_info": "Functional test contact"
        }

        # POST request to create a contact
        response = await client.post(
            "/api/contacts/",
            json=contact_data,
            headers={"Authorization": token}
        )

        # Assertions
        assert response.status_code == 201
        assert response.json()["first_name"] == "John"
        assert response.json()["email"] == "johndoe@example.com"
