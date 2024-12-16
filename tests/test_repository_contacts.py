import unittest
from unittest.mock import AsyncMock
from src.repository.contacts import create_contact
from src.schemas.contacts import ContactCreate
from src.database.models import User

class TestRepositoryContacts(unittest.IsolatedAsyncioTestCase):
    async def test_create_contact(self):
        # Mock data
        db_mock = AsyncMock()
        db_mock.add.return_value = None  
        db_mock.commit.return_value = None 
        
        user = User(id=1, email="user@example.com")
        contact_data = ContactCreate(
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            phone="1234567890",
            birthday=None,
            additional_info="Test contact"
        )

        # Call function
        result = await create_contact(contact_data, user, db_mock)

        # Assertions
        self.assertEqual(result.first_name, "John")
        self.assertEqual(result.email, "johndoe@example.com")
        db_mock.add.assert_called_once_with(result)  
        db_mock.commit.assert_called_once() 

if __name__ == "__main__":
    unittest.main()
