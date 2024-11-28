from datetime import datetime, timedelta
from typing import Optional, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.database.db import get_db
from src.schemas.users import TokenData
from src.conf.config import settings
from src.repository import users as repository_users

import uuid
import redis.asyncio as redis


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/auth/login")

class AuthService:
    def __init__(self):        
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = oauth2_scheme
        self.redis_client = redis.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}/0", 
            encoding="utf-8", 
            decode_responses=True
        )

    def get_password_hash(self, password: str) -> str:
        """Hashes a plain text password."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain password against a hashed password."""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_access_token(
        self, 
        data: Dict[str, str], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Creates a JWT access token with optional expiration."""
        to_encode = data.copy()
        
        # Generate a unique token ID to prevent token reuse
        token_id = str(uuid.uuid4())
        to_encode['jti'] = token_id

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        # Encode the token
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        
        # Store token in Redis for tracking and potential revocation
        await self.redis_client.setex(
            f"token:{token_id}", 
            settings.access_token_expire_minutes * 60, 
            "active"
        )
        
        return encoded_jwt

    async def create_email_verification_token(self, email: str) -> str:
        """Create a time-limited email verification token."""
        data = {"sub": email, "type": "email_verification"}
        expires_delta = timedelta(hours=1)  # Token valid for 1 hour
        
        return jwt.encode(
            {**data, "exp": datetime.utcnow() + expires_delta}, 
            settings.secret_key, 
            algorithm=settings.algorithm
        )

    async def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode a token."""
        try:
            # Decode the token
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=[settings.algorithm]
            )
            
            # Check if token is revoked in Redis
            token_id = payload.get('jti')
            if token_id and not await self.redis_client.exists(f"token:{token_id}"):
                return None
            
            return payload
        except JWTError:
            return None

    async def revoke_token(self, token: str):
        """Revoke a token by removing it from Redis."""
        try:
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=[settings.algorithm]
            )
            token_id = payload.get('jti')
            if token_id:
                await self.redis_client.delete(f"token:{token_id}")
        except JWTError:
            pass  # Token already invalid or cannot be decoded

async def get_current_user(
    self,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from the access token.
    
    Args:
        token: JWT access token
        db: Database session
    
    Returns:
        User object if authenticated
    
    Raises:
        HTTPException if authentication fails
    """
    try:
        # Verify the token
        payload = await self.verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract email from payload
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Fetch user from database
        user = await repository_users.get_user_by_email(email, db)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
auth_service = AuthService()