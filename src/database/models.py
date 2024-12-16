from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): The primary key.
        email (str): The user's email.
        password (str): The hashed password.
        username (str): The username.
        created_at (datetime): The account creation timestamp.
        confirmed (bool): Whether the user's email is confirmed.
        avatar_url (str): The URL of the user's avatar.
        refresh_token (str): The user's refresh token for authentication.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String(128), nullable=False)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=func.now())
    confirmed = Column(Boolean, default=False)
    avatar_url = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    contacts = relationship("Contact", back_populates="owner")


class Contact(Base):
    """Represents a contact belonging to a user.

    Attributes:
        id (int): The primary key.
        first_name (str): The contact's first name.
        last_name (str): The contact's last name.
        email (str): The contact's email.
        phone (str): The contact's phone number.
        birthday (datetime): The contact's date of birth.
        additional_info (str): Optional additional information.
        owner_id (int): The ID of the user who owns the contact.
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    birthday = Column(DateTime, nullable=True)
    additional_info = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="contacts")