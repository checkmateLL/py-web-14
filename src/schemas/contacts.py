from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date
from typing import Optional


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: Optional[date] = None
    additional_info: Optional[str] = None


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    birthday: Optional[date]
    additional_info: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    additional_info: Optional[str] = None


class ContactResponse(ContactBase):
    id: int

    class Config:
        config = ConfigDict(orm_mode=True)