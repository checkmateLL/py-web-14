import unittest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncResult

from src.repository.users import get_user_by_email, create_user
from src.schemas.users import UserCreate
from src.database.models import User


class TestRepositoryUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user_data = UserCreate(
            email="test@mail.com",
            password="hashed_password",
            username="testuser"
        )

    async def test_get_user_by_email_found(self):
        """Test retrieving a user by email when the user exists."""
        # Create a mock user
        existing_user = User(id=1, email=self.user_data.email, username="testuser")

        # Create a mock result
        mock_result = AsyncMock(spec=AsyncResult)
        mock_result.scalars.return_value.first.return_value = existing_user
        
        # Configure the session's execute method to return the mock result
        self.session.execute.return_value = mock_result

        # Call the function
        result = await get_user_by_email(self.user_data.email, self.session)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result.email, self.user_data.email)
        # Verify the query was called with the correct filter
        self.session.execute.assert_called_once()

    async def test_get_user_by_email_not_found(self):
        """Test retrieving a user by email when the user does not exist."""
        # Create a mock result that returns None
        mock_result = AsyncMock(spec=AsyncResult)
        mock_result.scalars.return_value.first.return_value = None
        
        # Configure the session's execute method to return the mock result
        self.session.execute.return_value = mock_result

        # Call the function
        result = await get_user_by_email("unknown@mail.com", self.session)

        # Assertions
        self.assertIsNone(result)
        self.session.execute.assert_called_once()

    async def test_create_user_existing_email(self):
        """Test that user creation fails if the email already exists."""
        # Create a mock user
        existing_user = User(id=1, email=self.user_data.email, username="existinguser")

        # Create a mock result that returns the existing user
        mock_result = AsyncMock(spec=AsyncResult)
        mock_result.scalars.return_value.first.return_value = existing_user
        
        # Configure the session's execute method to return the mock result
        self.session.execute.return_value = mock_result

        # Call the function and assert exception is raised
        with self.assertRaises(ValueError) as context:
            await create_user(self.user_data, self.session)

        self.assertEqual(str(context.exception), "User with this email already exists")
        self.session.add.assert_not_called()
        self.session.commit.assert_not_called()

    async def test_create_user_success(self):
        """Test that a new user is created successfully."""
        # Create a mock result that returns None (no existing user)
        mock_result = AsyncMock(spec=AsyncResult)
        mock_result.scalars.return_value.first.return_value = None
        
        # Configure the session's execute method to return the mock result
        self.session.execute.return_value = mock_result

        # Call the function
        result = await create_user(self.user_data, self.session)

        # Assertions
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertEqual(result.email, self.user_data.email)
        self.assertEqual(result.username, self.user_data.username)
        self.assertFalse(result.confirmed)  # Check that new user is not confirmed


if __name__ == '__main__':
    unittest.main()