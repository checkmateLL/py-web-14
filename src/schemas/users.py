from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str
    username: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    confirmed: bool

    class Config:
        model_config = ConfigDict(from_attributes=True)

class SignupResponse(BaseModel):
    user: UserResponse
    detail: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RequestEmail(BaseModel):
    email: str

class TokenData(BaseModel):
    email: str | None = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class LoginForm(BaseModel):
    email: str
    password: str