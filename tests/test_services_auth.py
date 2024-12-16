import unittest
from src.services.auth import AuthService

class TestAuthService(unittest.TestCase):
    def test_password_hashing(self):
        auth_service = AuthService()
        password = "password123"
        hashed_password = auth_service.hash_password(password)

        self.assertNotEqual(password, hashed_password)
        self.assertTrue(auth_service.verify_password(password, hashed_password))

    def test_verify_password_fail(self):
        auth_service = AuthService()
        password = "password123"
        wrong_password = "wrongpassword"
        hashed_password = auth_service.hash_password(password)

        self.assertFalse(auth_service.verify_password(wrong_password, hashed_password))

if __name__ == '__main__':
    unittest.main()
