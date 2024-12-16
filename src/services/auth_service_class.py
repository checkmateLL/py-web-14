from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

class AuthService:
    def __init__(self, secret_key: str, algorithm: str, access_token_expire_minutes: int):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
