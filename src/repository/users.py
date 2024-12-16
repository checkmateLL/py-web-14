from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound, IntegrityError
import logging

from src.database.models import User
from src.schemas.users import UserCreate, UserUpdate
from src.services.auth import auth_service
from src.services.email import email_service

logger = logging.getLogger(__name__)

async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    """
    Retrieve a user by their email address.

    Args:
        email (str): The email of the user.
        db (AsyncSession): The database session for querying.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    try:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error retrieving user by email {email}: {e}")
        return None

async def create_user(user: UserCreate, db: AsyncSession) -> User:
    """
    Create a new user.

    Args:
        user (UserCreate): The data for creating a new user.
        db (AsyncSession): The database session for querying.

    Returns:
        User: The newly created user object.

    Raises:
        ValueError: If a user with the email already exists.
    """
    try:
        # Check if user already exists
        existing_user = await get_user_by_email(user.email, db)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Hash the password
        hashed_password = auth_service.get_password_hash(user.password)

        new_user = User(
            email=user.email,
            username=user.username,
            password=hashed_password,
            confirmed=False 
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user
    except IntegrityError:
        await db.rollback()
        logger.error(f"Integrity error creating user: {user.email}")
        raise ValueError("Could not create user due to database constraint")
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error creating user: {e}")
        raise

async def get_user_by_id(user_id: int, db: AsyncSession) -> User | None:
    """
    Retrieve a user by their ID.
    """
    try:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().one()
        return user
    except NoResultFound:
        return None


async def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    db: AsyncSession
) -> User | None:
    """
    Update user details.

     Args:
        user_id (int): The ID of the user to update.
        user_update (UserUpdate): The fields to update.
        db (AsyncSession): The database session for querying.

    Returns:
        User | None: The updated user object, or None if user not found.

    Raises:
        ValueError: If the update fails due to an error.
    """
    try:
        user = await get_user_by_id(user_id, db)
        if not user:
            return None

        # Update only provided fields
        update_data = user_update.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            if key == 'password':
                # Hash new password if provided
                value = auth_service.get_password_hash(value)
            setattr(user, key, value)

        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user {user_id}: {e}")
        raise

async def confirm_email(email: str, db: AsyncSession) -> bool:
    """
    Confirm user's email address.

    Args:
        email (str): The user's email to confirm.
        db (AsyncSession): The database session for querying.

    Returns:
        bool: True if confirmation succeeded, otherwise False.
    """
    try:
        user = await get_user_by_email(email, db)
        if not user:
            return False

        user.confirmed = True
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        logger.error(f"Error confirming email for {email}: {e}")
        return False

async def request_password_reset(email: str, db: AsyncSession) -> str | None:
    """
    Generate a password reset token and optionally send reset email.
    """
    try:
        user = await get_user_by_email(email, db)
        if not user:
            return None

        # Generate a password reset token
        reset_token = await auth_service.create_email_verification_token(email)
        
        # Send password reset email
        reset_link = f"https://yourapp.com/reset-password?token={reset_token}"
        await email_service.send_email(
            email, 
            user.username, 
            subject="Password Reset Request",
            template_name="password_reset_template.html",
            template_body={
                "username": user.username,
                "reset_link": reset_link
            }
        )

        return reset_token
    except Exception as e:
        logger.error(f"Error in password reset request for {email}: {e}")
        return None

async def update_token(user: User, token: str, db: AsyncSession) -> None:
    """
    Updates the refresh token of a user in the database.
    """
    try:
        user.refresh_token = token
        await db.commit()
        await db.refresh(user)
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Failed to update refresh token: {e}")
