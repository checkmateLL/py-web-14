from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import os

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

    async def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7) 
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    async def create_email_verification_token(self, email: str) -> str:
        to_encode = {"sub": email}
        expire = datetime.utcnow() + timedelta(hours=1) 
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def get_email_from_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email = payload.get("sub")
            if email is None:
                raise ValueError("Token contains no email")
            return email
        except jwt.JWTError:
            raise ValueError("Invalid token")

# Initialize the auth service
SECRET_KEY = os.getenv("SECRET_KEY", "your_very_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

auth_service_instance = AuthService(
    secret_key=SECRET_KEY,
    algorithm=ALGORITHM,
    access_token_expire_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
)

def get_auth_service():
    return auth_service_instance